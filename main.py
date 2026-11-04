from fastapi import FastAPI
from pydantic import BaseModel,Field
class ChatRequest(BaseModel):
    message:str
class ChatResponse(BaseModel):
    answer:str
    model: str | None
    tokens : int
class QuizzRequest(BaseModel):
    subject:str = Field(...,min_length=3)
    number_quizzes : int = Field(...,lt=10,gt=1)
    number_options : int = Field(...,gt=2,lt=5)
class SummarizeRequest(BaseModel):
    topic:str
class FlashCardsRequest(BaseModel):
    topic:str
    number_flashcards: int
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
        "status":"ok","version":"0.1.0"
    }
@app.post("/chat",response_model=ChatResponse)
def chat(request:ChatRequest):
    return {
        "answer":f"You asked for {request.message}",
        "model":"placeholder",
        "toekens":0
    }
@app.post("/quizz")
def quizz(request:QuizzRequest):
    return {
        "topic":f"{request.subject}",
        "quizzes":[
            {
                "question":"fkdjkfdl",
                "options":["dfjkdhf","dfhkdj","fdjhdf","fjhkjd"],
                "correct_answer":0
            }
        ]
    }
@app.post("/summarize")
def summarize(request:SummarizeRequest):
    return {
        "topic":f"{request.topic}",
        "sumamry":"This is a summary"
    }
@app.post("/flashcard")
def flashcard(request:FlashCardsRequest):
    return {
        "topic":f"{request.topic}",
        "Flashcards":["dhfjksdh","hfdjk","hfdjkn","hdfjkn"]
    }