from fastapi import APIRouter,HTTPException
from .models import FlashCardsRequest,FlashCardsResponse
from app.services.flashcard import generate_flashcard
from app.services.ai import AIServiceError
from app.services.errors import ai_error_http
router = APIRouter(prefix="/flashcard",tags=["flashcards"])

@router.post("/",response_model=FlashCardsResponse)
def flashcard(request:FlashCardsRequest):
    try:
        clean_topic = request.topic.strip()
        response = generate_flashcard(request.topic,request.number_flashcards)
    except AIServiceError as error:
        raise ai_error_http(error)
    return response