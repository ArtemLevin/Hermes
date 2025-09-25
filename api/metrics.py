from time import perf_counter
from typing import Callable

from fastapi import APIRouter, Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# ===== Метрики =====
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=("method", "path", "status"),
)

HTTP_EXCEPTIONS = Counter(
    "http_exceptions_total",
    "Unhandled exceptions in requests",
    labelnames=("path",),
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency in seconds",
    labelnames=("method", "path"),
    # Разумные бакеты под dev/QA
    buckets=(0.025, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 2.0, 5.0),
)

# Бизнес-счётчики (используйте их в коде задач/почты)
JOBS_SENT = Counter("jobs_sent_total", "Queued background jobs", labelnames=("kind",))
MAIL_SENT = Counter("mail_sent_total", "Emails sent", labelnames=("template", "status"))

# ===== Middleware измерения =====
class MetricsMiddleware:
    """
    Измеряет латентность, считает запросы/ошибки.
    Приводит path к "статическому" виду (без query); роут-параметры остаются как есть.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope.get("method", "GET")
        path = scope.get("path", "/")

        start = perf_counter()
        status_holder = {"code": 500}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_holder["code"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            HTTP_EXCEPTIONS.labels(path=path).inc()
            HTTP_REQUESTS.labels(method=method, path=path, status="500").inc()
            raise
        finally:
            duration = perf_counter() - start
            REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
            HTTP_REQUESTS.labels(
                method=method, path=path, status=str(status_holder["code"])
            ).inc()

# ===== /metrics =====
router = APIRouter()

@router.get("/metrics")
def metrics() -> Response:
    content = generate_latest()
    return Response(content=content, media_type=CONTENT_TYPE_LATEST)
