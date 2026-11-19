from datetime import datetime
from fastapi import HTTPException,APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.services.db.database import get_db
from backend.app.services.db import crud


router = APIRouter(prefix="/conversations",tags = ["conversations"])
CURRENT_USER = 1
@router.get('/{conversation_id}/messages')
def read_messages(conversation_id:int,db: Session = Depends(get_db)):
    if crud.get_conversation(db,conversation_id,CURRENT_USER) is None:
        raise HTTPException(status_code=404,detail="Conversation not found")
    return crud.get_messages(db,conversation_id,CURRENT_USER)
    