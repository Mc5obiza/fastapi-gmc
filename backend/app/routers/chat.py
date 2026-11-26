from fastapi import HTTPException, APIRouter,Depends
from .models import ChatResponse,ChatRequest
from backend.app.services.ai import call_llm,AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.db.crud import add_message,get_messages,update_title
from backend.app.services.db.database import get_db
from backend.app.services.db import models
from backend.app.dependencies import get_current_user
from sqlalchemy.orm import Session
router = APIRouter(prefix="/chat",
                   tags = ["chat"])
@router.post("/",response_model=ChatResponse)
def chat(request:ChatRequest,db:Session = Depends(get_db),
         current_user:models.User = Depends(get_current_user)):
    history = []
    if request.conversation_id is not None:
        messages = get_messages(db,request.conversation_id,current_user.id)
        history = [{"role":msg.role,"content":msg.content} for msg in messages]
    clean_msg = request.message.strip()
    messages = history + [{"role":"user","content":clean_msg}]
    if not clean_msg:
        raise HTTPException(status_code=400,
                            detail="Message can not be empty")
    try:
        result = call_llm(messages)
        message_id,conversation_id = add_message(db,current_user.id,"user",clean_msg,conversation_id=request.conversation_id)
        convesation = update_title(db,current_user.id,conversation_id,result.title)
        message_id,conversation_id = add_message(db,current_user.id,"assistant",result.answer,conversation_id=conversation_id,tokens_used=result.tokens_used)
    except AIServiceError as error:
        raise ai_error_http(error)
    # return ChatResponse(**result)
    return result
   