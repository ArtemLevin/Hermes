"""Prometheus metrics instrumentation."""
from __future__ import annotations

from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app) -> None:  # type: ignore[no-untyped-def]
    Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)
