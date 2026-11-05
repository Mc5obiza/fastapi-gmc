from fastapi import FastAPI
from pydantic import BaseModel,Field
from datetime import datetime, timezone
class ChatRequest(BaseModel):
    message:str = Field(...,min_length=1, max_length=2000)
class QuizzRequest(BaseModel):
    subject:str = "Math"
    number_quizzes : int = Field(default = 3,ge=3,le=10)
    number_options : int  =3
class SummarizeRequest(BaseModel):
    text:str
    max_bullets:int = 3
class FlashCardsRequest(BaseModel):
    topic:str
    number_flashcards: int = 7
app = FastAPI()
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
@app.post("/chat")
def chat(request:ChatRequest):
    return {
        "answer":f"You asked for {request.message}",
        "model":"placeholder",
        "toekens":0
    }
@app.post("/quizz")
def quizz(request:QuizzRequest):
    questions = []
    for index in range(1,request.number_quizzes+1):
        questions.append(
            {
                "question":f"Question {index} about {request.subject}",
                "options": [f"Option {index+1}" for index in range(1,request.number_options+1)],
                "answer":"Option 1"
            }
        )
    return {
        "topic":request.subject,
        "num_questions":request.number_quizzes,
        "questions":questions
        }
@app.post("/summarize")
def summarize(request:SummarizeRequest):
    words = request.text.split()
    return {
        "summary":[
            "Normalement summary",
            "The Real summary"[:request.max_bullets],
            
        ],
        "word_count":len(words)
    }
@app.post("/flashcard")
def flashcard(request:FlashCardsRequest):
    return {
        "topic":f"{request.topic}",
        "Flashcards":["dhfjksdh","hfdjk","hfdjkn","hdfjkn"]
    }