"""Simple in-memory sliding window rate limiter."""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status


class SlidingWindowRateLimiter:
    """A cooperative, asyncio-safe sliding window rate limiter."""

    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> None:
        now = time.monotonic()
        async with self._lock:
            events = self._events[key]
            while events and now - events[0] > self.window_seconds:
                events.popleft()
            if len(events) >= self.limit:
                raise RateLimitExceeded(self.limit, self.window_seconds)
            events.append(now)


class RateLimitExceeded(Exception):
    def __init__(self, limit: int, window: int) -> None:
        self.limit = limit
        self.window = window
        super().__init__("Rate limit exceeded")


class RateLimitMiddleware:
    """Starlette middleware enforcing the rate limiter per client IP."""

    def __init__(self, app, limiter: SlidingWindowRateLimiter) -> None:  # type: ignore[no-untyped-def]
        self.app = app
        self.limiter = limiter

    async def __call__(self, scope, receive, send):  # type: ignore[no-untyped-def]
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        client_host = request.client.host if request.client else "anonymous"
        try:
            await self.limiter.check(client_host)
        except RateLimitExceeded as exc:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": exc.limit,
                    "window_seconds": exc.window,
                },
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
