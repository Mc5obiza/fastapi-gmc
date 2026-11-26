from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session
from backend.app.services.db import models
from backend.app.services.db.database import get_db
from backend.app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)
def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
                     db : Session = Depends(get_db)) -> models.User:
    error = HTTPException(status_code=401,
                          detail="Could not validate Credentials",
                          headers={'WWW-Authenticate': 'Bearer'})
    if credentials is None:
        raise error
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise error
    if payload["sub"] is None:
        raise error
    if db.get(models.RevokedToken,payload["jti"]) is not None:
        raise error
    user = db.get(models.User, payload["sub"])
    if user is None:
        raise error
    return user
