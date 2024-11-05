from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Inisialisasi pipeline BERT untuk analisis sentimen
# sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english", device=0)
sentiment_pipeline = pipeline("sentiment-analysis", model="w11wo/indonesian-roberta-base-sentiment-classifier", device=0)

class TextRequest(BaseModel):
    content: str

@app.post("/analyze-sentiment/")
async def analyze_sentiment(request: TextRequest):
    sentiment = sentiment_pipeline(request.content)
    return {"sentimentClass": sentiment[0]['label'], "score": sentiment[0]['score']}

# Menjalankan server: uvicorn app:app --reload
