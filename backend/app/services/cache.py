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
        decode_responses = True,
        socket_connect_timeout = 0.5,
        socket_timeout= 0.5,
        retry = Retry(NoBackoff(),5)
    )
_client = build_client(redis_url)
def get_client():
    return _client
def make_key(prefix, *parts):
    cleaned = (str(part).strip().lower().replace(" ","-") for part in parts)
    return prefix + ":" + ":".join(cleaned)
def cache_get(key):
    try:
        value = _client.get(key)
    except redis.RedisError:
        return None
    return json.loads(value) if value is not None else None
def cache_set(key,value,ttl = 3600):
    try:
        _client.set(key,json.dumps(value),ex=ttl)
    except redis.RedisError:
        pass
def cache_ping():
    try:
        return bool(_client.ping())
    except redis.RedisError:
        return False