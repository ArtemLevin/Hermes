"""Database engine and session management."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, get_settings


class Database:
    """Wrapper around SQLAlchemy async engine and session maker."""

    def __init__(self, settings: Settings) -> None:
        connect_args = {}
        pool_class = None
        if settings.database_url.startswith("sqlite+aiosqlite"):
            connect_args = {"check_same_thread": False}
            pool_class = StaticPool

        self.engine: AsyncEngine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            connect_args=connect_args,
            pool_pre_ping=True,
            poolclass=pool_class,  # type: ignore[arg-type]
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()


_database: Database | None = None


def get_database() -> Database:
    global _database
    if _database is None:
        _database = Database(get_settings())
    return _database


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    database = get_database()
    async with database.session() as session:
        yield session
