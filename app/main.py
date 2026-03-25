from fastapi import FastAPI
from app.recommender.schemas import FeatureInput, Recommendation
from app.recommender.service import generate_recommendations

app = FastAPI(title="MIoT Recommender API")


@app.get("/")
def read_root():
    return {"message": "MIoT Recommender API is running"}


@app.post("/recommendations", response_model=list[Recommendation])
def create_recommendations(features: FeatureInput):
    return generate_recommendations(features)