from fastapi import HTTPException
from .ai import AIServiceError

def ai_error_http(error:AIServiceError):
    if error.kind =="rate_limit":
        return HTTPException(status_code=429,detail=error.message)
    if error.kind == "auth":
        return HTTPException(status_code=500,detail=error.message)
    return HTTPException(status_code=500,detail="The AI Service failed. Please try again :3")