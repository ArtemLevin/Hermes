# api/deps.py
"""Infrastructure dependencies shared across the application."""
import os
from contextlib import contextmanager
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from api.models import Base

DEFAULT_SQLITE_URL = "sqlite:///./test.db"

def _ensure_sqlite_path(database_url: str) -> None:
    """Ensure parent directory exists for SQLite file."""
    if database_url.startswith("sqlite:///"):
        import pathlib
        db_path = database_url[10:]  # Remove 'sqlite:///'
        if db_path != ":memory:":
            pathlib.Path(db_path).parent.mkdir(parents=True, exist_ok=True)

def _create_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)
    _ensure_sqlite_path(database_url)

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        database_url,
        echo=False,  # Set to True for debugging
        pool_pre_ping=True,
        connect_args=connect_args,
    )

    # Create tables on startup - this is a simple approach, prefer migrations in production
    Base.metadata.create_all(bind=engine)
    return engine

def _create_async_engine():
    database_url = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)
    _ensure_sqlite_path(database_url)
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args,
        # For SQLite in tests, use StaticPool
        poolclass=StaticPool if database_url.startswith("sqlite") else None,
    )

# Sync engine and session
sync_engine = _create_engine()
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async engine and session
async_engine = _create_async_engine()
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

def get_db() -> Generator[Session, None, None]:
    """Dependency for sync database session."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async database session."""
    async with AsyncSessionLocal() as session:
        yield session