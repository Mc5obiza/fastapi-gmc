from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from datetime import datetime, timezone
from routers.models import (
    QuizzRequest,QuizzResponse,Quizz,
    FlashCard,FlashCardsResponse,FlashCardsRequest,
    SummarizeResponse,SummarizeRequest
    
)
from routers import chat,quizz
app = FastAPI()
app.include_router(chat.router)
app.include_router(quizz.router)
# Created an endpoint that runs root function
@app.get("/")
def root():
    return {
        "status":"ok",
        "message":"Welcome To the AI Assistant backend"
    }

@app.get("/about")
def about():
    return {
        "status":"ok",
        "Title":"AI Student assistant",
        "Description":"it helps students"
    }

@app.get("/health")
def health():
    return {
        "status":"ok",
        "message":"API IS RUNNING",
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "version":"0.2.0"
    }




@app.post("/summarize",response_model=SummarizeResponse)
def summarize(request:SummarizeRequest):
    words = request.text.split()
    return SummarizeResponse(
        summary=[
            "Normalement summary",
            "The Real summary"[:request.max_bullets],
            
        ],
        word_count=len(words)
    )

@app.post("/flashcard",response_model=FlashCardsResponse)
def flashcard(request:FlashCardsRequest):
    clean_topic = request.topic.strip()
    if not clean_topic:
        raise HTTPException(status_code=400,
                            detail="Topic can not be empty")
    flashcards = []
    for i in range(1,request.number_flashcards+1):
        flashcards.append(FlashCard(front=f"FlashCard {i}:dlkfhjdk",back=f"FlashCard {i}:djfgjdgf"))
    return FlashCardsResponse(
        topic=request.topic,
        flashcards=flashcards)