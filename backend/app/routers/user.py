from fastapi import HTTPException, APIRouter,Depends,Response
from .models import ChatResponse,ChatRequest
from backend.app.services.ai import call_llm,AIServiceError
from backend.app.services.errors import ai_error_http
from backend.app.services.db.crud import delete_user
from backend.app.services.db.database import get_db
from backend.app.services.db import models
from backend.app.dependencies import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/delete",tags=['delete'])
@router.delete("/")
def delete_user_rout(db: Session = Depends(get_db),
                current_user : models.User= Depends(get_current_user)):
    if not delete_user(db,current_user.id):
        raise HTTPException(status_code=404,detail="User not found")
    return Response(status_code=204)