from urllib.parse import urlparse
from uuid import uuid4
import shutil
import cv2
import boto3
import os
import json
import opensearch
import matrixsimilarity
import time

runtime = boto3.client('runtime.sagemaker')
sagemaker_endpoint = os.environ.get("SAGEMAKER_ENDPOINT")


def get_image_vector(filename: str):
    with open(filename, 'rb') as file:
        body = file.read()

    # Calculate time for SageMaker inference
    start_time = time.time()

    response = runtime.invoke_endpoint(
        EndpointName=sagemaker_endpoint, ContentType='application/x-image', Body=body)

    inference_time = time.time() - start_time
    # print(f"SageMaker inference took {inference_time:.2f} seconds")

    vector = json.loads(response['Body'].read())
    return vector


def get_video_vector(s3_url):
    temp_dir = os.path.join('/tmp', str(uuid4()))
    os.makedirs(temp_dir)

    try:
        parsed_url = urlparse(s3_url)
        bucket = parsed_url.netloc.split('.')[0]
        key = parsed_url.path.lstrip('/')

        original_filename = os.path.basename(key)
        video_path = os.path.join(temp_dir, original_filename)

        s3_client = boto3.client('s3')
        s3_client.download_file(bucket, key, video_path)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Failed to open video file: {original_filename}")

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if fps <= 0:
            raise Exception(f"Invalid FPS value: {fps}")

        frame_count = 0
        results = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % fps == 0:
                frame_path = os.path.join(temp_dir, f'frame_{frame_count}.jpg')
                cv2.imwrite(frame_path, frame)
                # Perform inference on the frame
                result = get_image_vector(frame_path)
                results.append({f'frame_{frame_count}': result})

            frame_count += 1

        cap.release()

        if not results:
            raise Exception("No frames were extracted from the video")

        return results

    except Exception as e:
        raise Exception(f"Error processing video: {str(e)}")

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def create_opensearch_index():
    return opensearch.create_index_with_knn()


def insert_video_vector(video_url):
    vector_array = get_video_vector(video_url)

    pending_documents = []
    for item in vector_array:
        for image, vector_item in item.items():
            tmp_document = {
                'file': video_url,
                'image': image,
                'vector': vector_item
            }
            pending_documents.append(tmp_document)

    sucess, errors = opensearch.bulk_insert_to_opensearch(pending_documents)
    if len(errors) > 0:
        print(errors)
        return False
    return sucess


def search_similarity_videos(video_url, size=10):
    video_vector = get_video_vector(video_url)

    similar_videos = {}
    for item in video_vector:
        for _, vector_item in item.items():
            search_result = opensearch.knn_search(vector_item, size)
            for hit in search_result['hits']['hits']:
                if hit['_source']['file'] in similar_videos:
                    similar_videos[hit['_source']['file']] += 1
                    continue
                similar_videos[hit['_source']['file']] = 1

    sorted_videos = sorted(similar_videos.items(),
                           key=lambda x: x[1],
                           reverse=True)
    sorted_videos = sorted_videos[:size]

    target_video_vectors = []
    for video in sorted_videos:
        file = video[0]
        target_vector = search_video_vector_by_file(file)
        if len(target_vector) == 0:
            continue
        print(len(target_vector))
        score = matrixsimilarity.calculate_video_vector_similarity(
            [list(d.values())[0] for d in video_vector], target_vector)
        target_video_vectors.append({
            'video_url': file,
            'score': score
        })

    target_video_vectors = sorted(target_video_vectors,
                                  key=lambda x: x['score'],
                                  reverse=True)
    return target_video_vectors


def search_video_vector_by_file(file):
    print(file)
    search_query = {
        "size": 500,
        "query": {
            "term": {
                "file.keyword": file
            }
        }
    }

    search_result = opensearch.search_documents(search_query)
    vector_arr = []
    for hit in search_result['hits']['hits']:
        vector_arr.append(hit['_source']['vector'])
    return vector_arr


def video_similarity(video_url_1, video_url_2):
    vector_1 = get_video_vector(video_url_1)
    vector_2 = get_video_vector(video_url_2)

    vector_1_arr = [list(d.values())[0] for d in vector_1]
    vector_2_arr = [list(d.values())[0] for d in vector_2]
    score = matrixsimilarity.calculate_video_vector_similarity(
        vector_1_arr, vector_2_arr)
    return {"score": score}
