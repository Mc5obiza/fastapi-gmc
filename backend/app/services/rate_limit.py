import redis
from fastapi import HTTPException
from backend.app.services.cache import get_client

def hit(key,limit,window):
    try:
        pipe = get_client().pipeline()
        pipe.set(key,0,ex=window, nx=True) # nx if the key exists don t create new key if it doesn t create new key
        pipe.incr(key)
        pipe.ttl(key)
        _,count,ttl = pipe.execute()
    except redis.RedisError:
        return True, 0
    return count <= limit, max(ttl,1)

def enforce(key,limit,window):
    allowed, retry_after = hit(key,limit,window)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too Many requests",
            headers={'Retry-After':str(retry_after)}
        )