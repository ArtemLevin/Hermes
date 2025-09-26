# api/rate_limit.py
import os
import time
import hashlib
from typing import Callable, Optional
import redis
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_r = redis.from_url(REDIS_URL)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Token bucket rate limiter using Redis.
    """
    def __init__(self, app, rate: float = 5.0, capacity: int = 10, key_fn: Optional[Callable[[Request], str]] = None):
        super().__init__(app)
        self.rate = rate
        self.capacity = capacity
        self.key_fn = key_fn or self._default_key_fn

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health, metrics, docs
        if request.url.path in ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        key = self.key_fn(request)
        current_time = time.time()

        # Lua script for atomic rate limiting
        lua_script = """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or current_time

        -- Calculate tokens to add based on elapsed time
        local elapsed = current_time - last_refill
        local new_tokens = math.min(capacity, tokens + elapsed * rate)

        if new_tokens >= 1 then
            new_tokens = new_tokens - 1
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', current_time)
            redis.call('EXPIRE', key, math.ceil(capacity / rate) + 1) -- Expire after bucket is empty
            return 0 -- OK
        else
            return 1 -- Rate limit exceeded
        end
        """

        script = _r.register_script(lua_script)
        try:
            result = script(keys=[key], args=[self.rate, self.capacity, current_time])
        except redis.RedisError:
            # If Redis is down, allow request to pass
            result = 0

        if result == 1:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        response = await call_next(request)
        return response

    def _default_key_fn(self, request: Request) -> str:
        """Generate a key based on client IP."""
        client_host = request.client.host
        return f"rate_limit:{hashlib.sha256(client_host.encode()).hexdigest()[:16]}"