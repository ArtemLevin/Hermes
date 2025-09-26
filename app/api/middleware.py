"""Custom ASGI middleware."""
from __future__ import annotations

from typing import Awaitable, Callable
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import bind_request_context, reset_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Bind request specific context and propagate request-id headers."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        bind_request_context(request_id=request_id, method=request.method, path=request.url.path)
        logger = structlog.get_logger(__name__)
        logger.info("request_started", method=request.method, path=request.url.path)
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed")
            reset_request_context()
            raise
        else:
            logger.info("request_completed", status_code=response.status_code)
            response.headers["X-Request-ID"] = request_id
            reset_request_context()
            return response
