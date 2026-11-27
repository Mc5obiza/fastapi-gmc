from fastapi import APIRouter, Depends,HTTPException,Response

from .models import FlashCardsRequest,FlashCardsResponse,FlashCard,FlashCardDeckSummary
from backend.app.services.flashcard import generate_flashcard
from backend.app.services.ai import AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.db import crud
from backend.app.services.cache import cache_get,cache_set,make_key
from backend.app.dependencies import get_current_user
from backend.app.services.db.models import User
from backend.app.services.db.crud import (
    add_deck,
    add_flashcard,
    get_all_flashcard_decks,
)
from backend.app.services.db.database import get_db
from sqlalchemy.orm import Session
from backend.app.services.rate_limit import enforce

router = APIRouter(prefix="/flashcard",tags=["flashcards"])

@router.post("/",response_model=FlashCardsResponse)
async def flashcard(request: FlashCardsRequest,http_response:Response,db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        enforce(f'flashcard:{current_user.id}',10,60)
        clean_topic = request.topic.strip()
        number = request.number_flashcards
        key = make_key("flashcard",clean_topic,number)
        cache = cache_get(key)
        if  cache is not None and not request.new:
            response = FlashCardsResponse(**cache)
            http_response.headers["X-Cache"] = "HIT"
        else:
            response = await generate_flashcard(clean_topic, request.number_flashcards)
            cache_set(key,response.model_dump())
            http_response.headers["X-Cache"] = "MISS"
            deck_id = add_deck(db, current_user.id, clean_topic)
            print(deck_id)
            for card in response.flashcards:
                add_flashcard(db, current_user.id, deck_id, card.front, card.back)
    except AIServiceError as error:
        raise ai_error_http(error)
    return response

@router.get("/", response_model=list[FlashCardDeckSummary])
def get_all_decks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    decks = get_all_flashcard_decks(db, current_user.id)
    return [
        FlashCardDeckSummary(id=deck.id, title=deck.title)
        for deck in decks
    ]

@router.get("/{deck_id}",response_model=FlashCardsResponse)
def get_flashcards(deck_id:int,db:Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deck = crud.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(status_code=404,detail="Flashcard deck not found")
    flashcards = crud.get_flashcards(db, deck_id, current_user.id)
    return FlashCardsResponse(
        topic = deck.title,
        flashcards = [FlashCard(front=card.front,back = card.back
                                ) for card in flashcards]
    )