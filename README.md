<p align="center">
    【 <a href="README.md">中文</a> | English】
</p>

# sample-for-video-similarity-using-serverless

## Project Background
Short video platforms are prevalent, producing a large number of videos daily. There exists an issue of creators misappropriating others' videos, necessitating technical means to identify similar videos.

Traditional identification methods typically rely on manual detection and simple applications, such as identifying video titles or descriptions. However, with the generation of massive data, such methods cannot efficiently process and comply with non-circular and non-personal requirements. To address these issues, this project was launched to implement automatic video similarity detection through an efficient unified identification model.

---

## Implementation Principles
### Video Similarity Comparison
1. Video Frame Extraction: Use OpenCV for uniform frame extraction from videos
2. Feature Extraction: Utilize pre-trained ResNet50 model to convert each frame into a 1000-dimensional feature vector
3. Vector Matrix Calculation: Form matrices from feature vectors of all frames
4. Similarity Calculation: Calculate similarity scores between two videos using algorithms like cosine similarity

### Similar Video Retrieval
1. Vector Storage: Store video feature vectors in Amazon OpenSearch vector database
2. Approximate Retrieval: Use KNN algorithm for efficient vector similarity retrieval
3. Secondary Sorting: Perform precise similarity calculation on retrieval results for final ranking

---

## Project Architecture
![architecture](./assets/video-similarity-architecture.png)

---

## Operation Guide

### 1. Subscribe and Deploy ResNet50 on AWS Marketplace
Subscription link: [ResNet50 Subscription](https://aws.amazon.com/marketplace/ai/procurement?productId=cc879d3b-e759-4270-9afb-ceb50d2f7fe6)

1) After deployment, remember the SageMaker Endpoint Name;

### 2. CDK One-Click Deployment
1) Install AWS CDK: Please refer to [CDK Installation Guide](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
2) Clone project locally and deploy using CDK:
```bash
cd src/cdk
# Example: Specify SageMaker endpoint
cdk deploy --parameters sagemaker_endpoint=ResNet50
```
3) Get API Gateway Endpoint;
4) Create OpenSearch index:
```bash
curl --location 'https://{{apigateway.endpoint.url}}/create_opensearch_index' \
--header 'Content-Type: text/plain' \
--data '{}'
```

---

## API Documentation

### Get Video Vector
* **Path**: `/get_video_vector`
* **Method**: POST
* **Request Params**:
```json
{
    "video_url": "s3://your_bucket/test.mp4"
}
```
* **Response**:
```json
{
    "video_vectors": {
        "image_001": [0.2212321, 0.2212321...],
        "image_002": [0.2212321, 0.2212321...],
        ...
    }
}
```

### Insert Video Vector into Vector Database
* **Path**: `/insert_video_vector`
* **Method**: POST
* **Request Params**:
```json
{
    "video_url": "s3://your_bucket/test.mp4"
}
```
* **Response**:
```json
{"result": 136}
```

### Search Similar Videos
* **Path**: `/search_similarity_videos`
* **Method**: GET
* **Request Params**:
```json
{
    "video_url": "s3://your_bucket/test.mp4",
    "size": 10
}
```
* **Response**:
```json
{
    "videos": [
        {
            "video_url": "s3://your_bucket/test.mp4",
            "score": 0.99
        },
        {
            "video_url": "s3://your_bucket/test.mp4",
            "score": 0.99
        },
        ...
    ]
}
```

### Compare Two Videos Similarity
* **Path**: `/video_similarity`
* **Method**: POST
* **Request Params**:
```json
{
    "video_url_1": "s3://your_bucket/test.mp4",
    "video_url_2": "s3://your_bucket/test.mp4"
}
```
* **Response**:
```json
{
    "score": 0.92
}
```

---

## FAQ

1. **Why choose ResNet50 model?**
   ResNet50 is a well-proven balanced model with excellent image classification and feature extraction capabilities, suitable for video vectorization tasks.

2. **Does OpenSearch support encrypted search?**
   Yes, it supports data security through encrypted channels (HTTPS) and access control features.

3. **How to maintain video original files and vector data?**
   Recommend using Amazon S3 for video storage and Lambda for real-time invocation and vector addition.

## Contribution Guidelines

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
