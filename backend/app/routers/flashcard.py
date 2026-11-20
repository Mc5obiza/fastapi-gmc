from fastapi import APIRouter, Depends,HTTPException

from .models import FlashCardsRequest,FlashCardsResponse,FlashCard,FlashCardDeckSummary
from backend.app.services.flashcard import generate_flashcard
from backend.app.services.ai import AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.db import crud
from backend.app.services.db.crud import (
    add_deck,
    add_flashcard,
    get_all_flashcard_decks,
)
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

@router.get("/", response_model=list[FlashCardDeckSummary])
def get_all_decks(db: Session = Depends(get_db)):
    decks = get_all_flashcard_decks(db, CURRENT_USER)
    return [
        FlashCardDeckSummary(id=deck.id, title=deck.title)
        for deck in decks
    ]

@router.get("/{deck_id}",response_model=FlashCardsResponse)
def get_flashcards(deck_id:int,db:Session = Depends(get_db)):
    deck = crud.get_deck(db, deck_id, CURRENT_USER)
    if not deck:
        raise HTTPException(status_code=404,detail="Flashcard deck not found")
    flashcards = crud.get_flashcards(db, deck_id, CURRENT_USER)
    return FlashCardsResponse(
        topic = deck.title,
        flashcards = [FlashCard(front=card.front,back = card.back
                                ) for card in flashcards]
    )