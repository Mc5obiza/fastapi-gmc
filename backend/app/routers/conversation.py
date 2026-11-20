from datetime import datetime
from fastapi import HTTPException,APIRouter,Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from backend.app.services.db.database import get_db
from backend.app.services.db import crud


router = APIRouter(prefix="/conversations",tags = ["conversations"])
CURRENT_USER = 1

class ConversationSummary(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=list[ConversationSummary])
def read_conversations(db: Session = Depends(get_db)):
    return crud.get_all_cnv(db, CURRENT_USER)

@router.get('/{conversation_id}/messages')
def read_messages(conversation_id:int,db: Session = Depends(get_db)):
    if crud.get_conversation(db,conversation_id,CURRENT_USER) is None:
        raise HTTPException(status_code=404,detail="Conversation not found")
    return crud.get_messages(db,conversation_id,CURRENT_USER)
    