from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import videosimilarity

app = FastAPI()


class VideoRequest(BaseModel):
    video_url: str


class SearchRequest(BaseModel):
    video_url: str
    size: int = 10


class VideoSimilarityRequest(BaseModel):
    video_url_1: str
    video_url_2: str


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.post("/get_video_vector")
def get_web_content(request: VideoRequest):
    return videosimilarity.get_video_vector(request.video_url)


@app.post("/create_opensearch_index")
def create_opensearch_index():
    return {'result': videosimilarity.create_opensearch_index()}


@app.post("/insert_video_vector")
def insert_video_vector(request: VideoRequest):
    return {'result': videosimilarity.insert_video_vector(request.video_url)}


@app.post("/search_similarity_videos")
def search_similarity_videos(request: SearchRequest):
    return videosimilarity.search_similarity_videos(request.video_url, request.size)


@app.post("/video_similarity")
def video_similarity(request: VideoSimilarityRequest):
    return videosimilarity.video_similarity(request.video_url_1, request.video_url_2)
