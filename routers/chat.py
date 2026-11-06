from fastapi import HTTPException, APIRouter
from .models import ChatResponse,ChatRequest
from services.ai import call_llm,AIServiceError
from services.errors import ai_error_http
router = APIRouter(prefix="/chat",
                   tags = ["chat"])
@router.post("/",response_model=ChatResponse)
def chat(request:ChatRequest):
    clean_msg = request.message.strip()
    if not clean_msg:
        raise HTTPException(status_code=400,
                            detail="Message can not be empty")
    try:
        result = call_llm(clean_msg)
    except AIServiceError as error:
        raise ai_error_http(error)
    # return ChatResponse(**result)
    return ChatResponse(
        answer = result["answer"],
        model = result["model"],
        tokens_used = result["tokens_used"]
    )