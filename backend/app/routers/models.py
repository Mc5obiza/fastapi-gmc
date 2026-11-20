from pydantic import BaseModel,Field,EmailStr,field_validator
from datetime import datetime
class ChatRequest(BaseModel):
    message:str = Field(...,min_length=1, max_length=2000)
    conversation_id: int | None = None
class ChatResponse(BaseModel):
    answer: str
    model:str
    tokens_used:int
    conversation_id: int | None = None

class QuizzRequest(BaseModel):
    subject:str = Field(...,min_length=2,max_length=100)
    number_quizzes : int = Field(default = 3,ge=3,le=10)
    number_options : int = Field(default = 4,ge=4,le=6)

class Quizz(BaseModel):
    question:str
    options : list[str]
    correct:int

class QuizzResponse(BaseModel):
    topic : str
    nb_questions : int
    quizz : list[Quizz]

class QuizDetailResponse(BaseModel):
    id: int
    topic: str
    nb_questions: int
    quizz: list[Quizz]

class FlashCardDeckSummary(BaseModel):
    id: int
    title: str

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
class RegisterRequest(BaseModel):
    email : EmailStr
    password: str
    confirm_password : str
    @field_validator('password')
    @classmethod
    def check_password(cls,value):
        if len(value) < 8:
            raise ValueError("Password must be contain at least 8 characters")
        if len(value) > 30:
            raise ValueError("Password is too long")
        return value
class LoginRequest(BaseModel):
    email:EmailStr
    password:str
class UserOut(BaseModel):
    id : int
    email: EmailStr
    created_at : datetime
