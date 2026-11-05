from fastapi import HTTPException, APIRouter
from .models import ChatResponse,ChatRequest
router = APIRouter(prefix="/chat",
                   tags = ["chat"])
@router.post("/",response_model=ChatResponse)
def chat(request:ChatRequest):
    clean_msg = request.message.strip()
    if not clean_msg:
        raise HTTPException(status_code=400,
                            detail="Message can not be empty")
    return ChatResponse(
        answer="fdjlkdhfhflkd",
        model="EMPTY",
        tokens_used=0
    )