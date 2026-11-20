from fastapi import APIRouter, Depends,HTTPException

from backend.app.services.db import models
from .models import FlashCardsRequest,FlashCardsResponse,FlashCard
from backend.app.services.flashcard import generate_flashcard
from backend.app.services.ai import AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.db.crud import add_deck, add_flashcard
from backend.app.services.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/flashcard",tags=["flashcards"])
CURRENT_USER = 1

@router.post("/",response_model=FlashCardsResponse)
def flashcard(request: FlashCardsRequest, db: Session = Depends(get_db)):
    try:
        clean_topic = request.topic.strip()
        response = generate_flashcard(clean_topic, request.number_flashcards)
        deck_id = add_deck(db, CURRENT_USER, clean_topic)
        print(deck_id)
        for card in response.flashcards:
            add_flashcard(db, CURRENT_USER, deck_id, card.front, card.back)
    except AIServiceError as error:
        raise ai_error_http(error)
    return response
@router.get("/{deck_id}",response_model=FlashCardsResponse)
def get_flashcards(deck_id:int,db:Session = Depends(get_db)):
    deck = db.query(models.FlashCardDeck).filter(
        models.FlashCardDeck.id == deck_id,
        models.FlashCardDeck.user_id == CURRENT_USER
    ).first()
    if not deck:
        raise HTTPException(status_code=404,detail="Flashcard deck not found")
    flashcards = db.query(models.FlashCard).filter(
        models.FlashCard.deck_id == deck_id
    ).all()
    return FlashCardsResponse(
        topic = deck.title,
        flashcards = [FlashCard(front=card.front,back = card.back
                                ) for card in flashcards]
    )