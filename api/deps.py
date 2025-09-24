"""Infrastructure dependencies shared across the application."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from fastapi import Query
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


DEFAULT_SQLITE_URL = "sqlite:///./storage/hermes.db"


def _ensure_sqlite_path(database_url: str) -> None:
    """Create a directory for SQLite DBs before engine initialisation."""

    if not database_url.startswith("sqlite"):
        return

    db_path = database_url.split("///", maxsplit=1)[-1]
    if not db_path:
        return

    # ``sqlite:///:memory:`` не требует подготовки, а обычные файлы — да.
    if db_path == ":memory:":
        return

    Path(db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def _create_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)
    _ensure_sqlite_path(database_url)

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

    try:
        return create_engine(
            database_url,
            future=True,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    except SQLAlchemyError as exc:  # pragma: no cover - защитное поведение
        # Исключение перехватывается, чтобы сообщить более осмысленную ошибку при старте.
        msg = f"Unable to initialise database engine for URL {database_url!r}: {exc}"
        raise RuntimeError(msg) from exc


if not (__package__ or "").startswith("api."):
    import models as models_module  # type: ignore
else:  # pragma: no cover - ветка для запуска как пакет
    from . import models as models_module


engine = _create_engine()
SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)
models_module.Base.metadata.create_all(bind=engine)


def get_db() -> Iterable[Session]:
    """FastAPI dependency returning a scoped SQLAlchemy session."""

    with SessionLocal() as session:
        yield session

class Page:
    """Simple pagination descriptor with sane defaults and bounds."""

    def __init__(self, page: int = 1, size: int = 20, max_size: int = 100):
        self.page = max(page, 1)
        self.size = min(max(size, 1), max_size)

def pagination(
    page: int = Query(1, ge=1, description="Номер страницы (>= 1)"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы (1..100)"),
) -> Page:
    """Factory dependency that clamps incoming pagination parameters."""

    return Page(page, size)
