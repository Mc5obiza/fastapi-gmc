from fastapi import HTTPException, APIRouter,Depends
from .models import ChatResponse,ChatRequest
from backend.app.services.ai import call_llm,AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.db.crud import add_message,get_messages
from backend.app.services.db.database import get_db
from sqlalchemy.orm import Session
router = APIRouter(prefix="/chat",
                   tags = ["chat"])
CURRENT_USER = 1
@router.post("/",response_model=ChatResponse)
def chat(request:ChatRequest,db:Session = Depends(get_db)):
    history = []
    if request.conversation_id is not None:
        messages = get_messages(db,request.conversation_id,CURRENT_USER)
        history = [{"role":msg.role,"content":msg.content} for msg in messages]
    clean_msg = request.message.strip()
    messages = history + [{"role":"user","content":clean_msg}]
    message_id,conversation_id = add_message(db,CURRENT_USER,"user",clean_msg,conversation_id=request.conversation_id)
    print(conversation_id)
    if not clean_msg:
        raise HTTPException(status_code=400,
                            detail="Message can not be empty")
    try:
        result = call_llm(messages)
        message_id,conversation_id = add_message(db,CURRENT_USER,"assistant",result["answer"],conversation_id=conversation_id,tokens_used=result["tokens_used"])
    except AIServiceError as error:
        raise ai_error_http(error)
    # return ChatResponse(**result)
    return ChatResponse(
        answer = result["answer"],
        model = result["model"],
        tokens_used = result["tokens_used"],
        conversation_id = conversation_id,
    )