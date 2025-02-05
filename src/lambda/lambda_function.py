import videosimilarity
import json


def lambda_handler(event, context):
    print(event)

    path = event['rawPath']
    body = event['body']
    request_body = json.loads(body)
    if path.endswith('get_video_vector'):
        video_url = request_body['video_url']
        return {'result': videosimilarity.get_video_vector(video_url)}
    elif path.endswith('insert_video_vector'):
        video_url = request_body['video_url']
        return {'result': videosimilarity.insert_video_vector(video_url)}
    elif path.endswith('search_similarity_videos'):
        video_url = request_body['video_url']
        size = request_body['size']
        return videosimilarity.search_similarity_videos(video_url, size)
    elif path.endswith('video_similarity'):
        video_url_1 = request_body['video_url_1']
        video_url_2 = request_body['video_url_2']
        return videosimilarity.video_similarity(video_url_1, video_url_2)
    elif path.endswith('create_opensearch_index'):
        return {'result': videosimilarity.create_opensearch_index()}
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('invalid path')
        }
