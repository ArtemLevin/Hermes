# api/metrics.py
import time
from collections import Counter
from prometheus_client import Counter as PromCounter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

REQUEST_COUNT = PromCounter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        endpoint = self._get_endpoint_name(request)

        response = await call_next(request)

        status_code = response.status_code
        duration = time.time() - start_time

        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_LATENCY.observe(duration)

        return response

    def _get_endpoint_name(self, request: Request) -> str:
        """Generate a static endpoint name for Prometheus metrics."""
        for route in request.app.router.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return f"{route.methods}_{route.path}"
        return "unknown"

# Metrics router
from fastapi import APIRouter

router = APIRouter()

@router.get("/", response_class=Response)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)