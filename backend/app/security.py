import bcrypt
from dotenv import load_dotenv
import jwt
from datetime import datetime,timedelta,timezone
import os
from uuid import uuid4
load_dotenv()
secret = os.getenv("JWT_SECRET_KEY")
if not secret:
    raise RuntimeError("JWT SECRET is not set")
def create_access_token(user_id:int,expires_minute: int = 60)->str:
    minutes = expires_minute
    payload = {
        "sub":str(user_id),
        "exp":datetime.now(timezone.utc) + timedelta(minutes=minutes),
        "jti":uuid4().hex
    }
    return jwt.encode(payload,secret,algorithm="HS256")
def decode_access_token(token:str) -> dict | None:
    try:
        payload = jwt.decode(token,secret,algorithms=["HS256"])
        payload["sub"] = int(payload["sub"])
        if 'jti' not in payload:
            return None
        return payload
    except (jwt.PyJWTError,KeyError,ValueError):
        return None
def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
def verify_password(password:str, password_hash:str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(),password_hash.encode())
    except ValueError:
        return False