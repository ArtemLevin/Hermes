import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pythonjsonlogger import jsonlogger

# ===== Correlation ID (request-id) =====
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)

REQUEST_ID_HEADER = "X-Request-ID"

def get_request_id() -> str | None:
    return _request_id.get()

def _generate_request_id() -> str:
    return str(uuid.uuid4())

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Устанавливает/прокидывает correlation id.
    - Читает X-Request-ID из входящего запроса (если есть).
    - Генерирует новый, если отсутствует.
    - Прокидывает в контекст и в ответные заголовки.
    - Пишет access-лог в JSON со статусом/временем.
    """
    def __init__(self, app, logger: logging.Logger | None = None) -> None:
        super().__init__(app)
        self.logger = logger or logging.getLogger("api.access")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        rid = request.headers.get(REQUEST_ID_HEADER) or _generate_request_id()
        token = _request_id.set(rid)
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            self.logger.info(
                "request_complete",
                extra={
                    "request_id": rid,
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "status_code": getattr(response, "status_code", 0),
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                },
            )
            _request_id.reset(token)
        response.headers[REQUEST_ID_HEADER] = rid
        return response

# ===== JSON logging setup =====

class RequestIdFilter(logging.Filter):
    """Добавляет request_id в каждый лог-запись из контекста."""
    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, "request_id", get_request_id())
        return True

def setup_json_logging(level: int = logging.INFO) -> None:
    """
    Инициализирует JSON-логирование для корневого логгера и uvicorn-логгеров.
    """
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    fmt = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s"
    )
    handler.setFormatter(fmt)
    handler.addFilter(RequestIdFilter())

    # очистим существующие хэндлеры и установим наш
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)

    # uvicorn/access → тоже в JSON
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True
        lg.setLevel(level)

    # отдельный логгер для access-сообщений из мидлвари
    access_logger = logging.getLogger("api.access")
    access_logger.setLevel(level)
    access_logger.handlers = [handler]
    access_logger.propagate = False
