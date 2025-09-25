import os
import time
import hashlib
from typing import Callable, Optional

import redis
from fastapi import Request, Response, HTTPException

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_r = redis.from_url(REDIS_URL)

class RateLimitMiddleware:
    """
    Простой token-bucket в Redis.
    Параметры:
      - rate: скорость пополнения (токенов в секунду)
      - capacity: размер ведра
      - key_fn: функция формирования ключа (по умолчанию IP; можно по токену)
      - include_paths / exclude_paths: фильтры по путям
    """

    LUA = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])
    local capacity = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])
    local ttl = tonumber(ARGV[5])

    local data = redis.call("HMGET", key, "tokens", "ts")
    local tokens = tonumber(data[1])
    local ts = tonumber(data[2])

    if tokens == nil then
        tokens = capacity
        ts = now
    end

    local delta = math.max(0, now - ts)
    local filled = math.min(capacity, tokens + delta * rate)
    local allowed = 0
    if filled >= requested then
        tokens = filled - requested
        allowed = 1
    else
        tokens = filled
        allowed = 0
    end

    redis.call("HMSET", key, "tokens", tokens, "ts", now)
    redis.call("EXPIRE", key, ttl)
    return {allowed, tokens}
    """

    def __init__(
        self,
        app,
        rate: float = 5.0,      # 5 rps
        capacity: int = 20,     # burst=20
        requested: int = 1,
        ttl_seconds: int = 60,
        include_paths: Optional[list[str]] = None,
        exclude_paths: Optional[list[str]] = None,
        key_fn: Optional[Callable[[Request], str]] = None,
    ):
        self.app = app
        self.rate = rate
        self.capacity = capacity
        self.requested = requested
        self.ttl = ttl_seconds
        self.include_paths = include_paths or []
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
        self.key_fn = key_fn or self._key_by_ip
        self._script = _r.register_script(self.LUA)

    def _key_by_ip(self, req: Request) -> str:
        ip = req.client.host if req.client else "unknown"
        return "rl:" + hashlib.sha1(ip.encode()).hexdigest()

    def _should_check(self, path: str) -> bool:
        if any(path.startswith(p) for p in self.exclude_paths):
            return False
        if self.include_paths:
            return any(path.startswith(p) for p in self.include_paths)
        return True  # если include пуст — лимитируем всё, кроме исключений

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "/")
        if not self._should_check(path):
            return await self.app(scope, receive, send)

        # формируем ключ
        req = Request(scope, receive=receive)
        key = self.key_fn(req)

        now = int(time.time())
        allowed, tokens = self._script(
            keys=[key],
            args=[now, self.rate, self.capacity, self.requested, self.ttl],
        )

        if int(allowed) == 1:
            # прокидываем оставшиеся токены в заголовки ответа
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = message.setdefault("headers", [])
                    headers.append((b"x-rate-remaining", str(int(tokens)).encode()))
                await send(message)
            return await self.app(scope, receive, send_wrapper)
        else:
            # 429 Too Many Requests
            resp = Response(
                content='{"detail":"Too Many Requests"}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "1"},
            )
            return await resp(scope, receive, send)
