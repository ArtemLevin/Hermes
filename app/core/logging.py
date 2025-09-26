"""Structured logging configuration."""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from .config import Settings


def _configure_stdlib_logging(level: str) -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )


def setup_logging(settings: Settings) -> None:
    """Configure structlog with JSON output and contextual request data."""

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            timestamper,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(settings.log_level)),
        cache_logger_on_first_use=True,
    )

    _configure_stdlib_logging(settings.log_level)


def bind_request_context(request_id: str, **extra: Any) -> None:
    """Bind request specific context for all subsequent log entries."""

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, **extra)


def reset_request_context() -> None:
    """Reset context variables when a request completes."""

    structlog.contextvars.clear_contextvars()
