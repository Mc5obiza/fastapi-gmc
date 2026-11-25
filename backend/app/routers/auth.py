from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.app.services.db import crud
from backend.app.services.db.database import get_db
from .models import LoginRequest, RegisterRequest, UserOut,TokenResponse
from backend.app.security import hash_password,verify_password,create_access_token
from datetime import datetime
from backend.app.dependencies import get_current_user
from backend.app.services.db import models
router = APIRouter(prefix="/auth",tags=['auth'])

@router.post("/register",response_model=TokenResponse,status_code=201)
def register(request:RegisterRequest,db:Session = Depends(get_db)):
    email = request.email.lower()
    if crud.lookup_by_email(db,email) is not None:
        raise HTTPException(status_code=409,detail="Email alreadt registred")
    if request.password != request.confirm_password:
        raise HTTPException(status_code=412,detail="It s not the same password")
    password_hash = hash_password(request.password)
    user_id = crud.add_user(db,email,password_hash)   
    return TokenResponse(access_token=create_access_token(user_id=user_id))
@router.post("/login",response_model=TokenResponse)
def login(request:LoginRequest,db:Session = Depends(get_db)):
    user = crud.lookup_by_email(db,request.email.lower())
    if user is None or not verify_password(request.password,user.password_hash):
        raise HTTPException(status_code=401,detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))
@router.get("/me",response_model=UserOut)
def me(current_user:models.User = Depends(get_current_user)):
    return current_user

