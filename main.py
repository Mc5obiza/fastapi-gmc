from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from datetime import datetime, timezone
class ChatRequest(BaseModel):
    message:str = Field(...,min_length=1, max_length=2000)
class ChatResponse(BaseModel):
    answer: str
    model:str
    tokens_used:int
class QuizzRequest(BaseModel):
    subject:str = Field(...,min_length=2,max_length=100)
    number_quizzes : int = Field(default = 3,ge=3,le=10)
    number_options : int = Field(default = 4,ge=4,le=6)
class Quizz(BaseModel):
    question:str
    options : list[str]
    correct:str
class QuizzResponse(BaseModel):
    topic : str
    nb_questions : int
    quizz : list[Quizz]
class SummarizeRequest(BaseModel):
    text: str = Field(min_length=20, max_length=5000)
    max_bullets:int = Field(default=3,ge=3,le = 10)
class SummarizeResponse(BaseModel):
    summary : list[str]
    word_count : int
class FlashCardsRequest(BaseModel):
    topic:str = Field(...,min_length=3,max_length=10)
    number_flashcards: int = Field(default=7,ge = 7, le = 18)
class FlashCard(BaseModel):
    front:str
    back:str
class FlashCardsResponse(BaseModel):
    topic : str
    flashcards : list[FlashCard]
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
@app.post("/chat",response_model=ChatResponse)
def chat(request:ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400,
                            detail = "Message can not be Empty")
    return ChatResponse(
        answer="dfghjdgfjhdgdfhjgdjhf",
        model="PlaceHolder",
        tokens_used=0
    )
@app.post("/quizz",response_model=QuizzResponse)
def quizz(request:QuizzRequest):
    questions = []
    for index in range(1,request.number_quizzes+1):
        questions.append(
        Quizz(
                question=f"Question {index} about {request.subject}",
                options= [f"Option {index+1}" for index in range(1,request.number_options+1)],
                correct="Option 1"
        )
        )
    return QuizzResponse(
        topic=request.subject,
        nb_questions=request.number_quizzes,
        quizz=questions
    )
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