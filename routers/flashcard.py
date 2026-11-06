from fastapi import APIRouter,HTTPException
from .models import FlashCard,FlashCardsRequest,FlashCardsResponse

router = APIRouter(prefix="/flashcard",tags=["flashcards"])

@router.post("/",response_model=FlashCardsResponse)
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