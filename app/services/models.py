from pydantic import BaseModel,Field
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