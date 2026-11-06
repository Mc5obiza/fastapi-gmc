from fastapi import APIRouter, HTTPException
from .models import SummarizeRequest,SummarizeResponse

router = APIRouter(prefix="/summarize",tags=['summarize'])

@router.post("/",response_model=SummarizeResponse)
def summarize(request:SummarizeRequest):
    words = request.text.split()
    return SummarizeResponse(
        summary=[
            "Normalement summary",
            "The Real summary"[:request.max_bullets],
            
        ],
        word_count=len(words)
    )
