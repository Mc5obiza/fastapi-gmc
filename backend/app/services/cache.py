import os
import json

import redis
from redis.backoff import NoBackoff
from redis.retry import Retry
from dotenv import load_dotenv

load_dotenv()
redis_url = os.getenv("REDIS_URL")

def build_client(url):
    return redis.Redis.from_url(
        url,
        decode_response = True,
        socket_connect_timeout = 0.5,
        socket_timeout= 0.5,
        retry = Retry(NoBackoff(),5)
    )
_client = build_client(redis_url)

def make_key(prefix, *parts):
    cleaned = (str(part).strip().lower().replace(" ","-") for part in parts)
    return prefix + ":" + ":".join(cleaned)