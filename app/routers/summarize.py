from fastapi import APIRouter, HTTPException
from .models import SummarizeRequest,SummarizeResponse
from app.services.summarize import generate_summarize
from app.services.errors import ai_error_http
from app.services.ai import AIServiceError
router = APIRouter(prefix="/summarize",tags=['summarize'])

@router.post("/",response_model=SummarizeResponse)
def summarize(request:SummarizeRequest):
    try:
        max_bulltets = request.max_bullets
        text = request.text.strip()
        response = generate_summarize(text,max_bulltets)
    except AIServiceError as error:
        raise ai_error_http(error)
    return response