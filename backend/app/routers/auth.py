from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.app.services.db import crud
from backend.app.services.db.database import get_db
from .models import LoginRequest, RegisterRequest, UserOut
from backend.app.security import hash_password
from datetime import datetime
router = APIRouter(prefix="/auth",tags=['auth'])

@router.post("/register",response_model=UserOut,status_code=201)
def register(request:RegisterRequest,db:Session = Depends(get_db)):
    email = request.email.lower()
    if crud.lookup_by_email(db,email) is not None:
        raise HTTPException(status_code=409,detail="Email alreadt registred")
    try:
        if request.password != request.confirm_password:
            raise HTTPException(status_code=412,detail="It s not the same password")
        return UserOut(id=crud.add_user(db,email,hash_password(request.password)),email=email,created_at=datetime.now())
    except:
        db.rollback()
        raise HTTPException(status_code=500,detail="Internal ERROR")