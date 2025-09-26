"""OpenTelemetry tracing configuration."""
from __future__ import annotations

from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine

from .config import Settings


def configure_tracing(settings: Settings, engine: Optional[AsyncEngine] = None) -> None:
    """Initialise OpenTelemetry tracing if configured."""

    if not settings.otlp_endpoint:
        return

    resource = Resource.create({"service.name": settings.app_name, "service.environment": settings.environment})
    provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument()
    if engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
