"""Pytest fixtures for API tests."""
from __future__ import annotations

import asyncio
import os
from typing import AsyncIterator

import pytest
from httpx import AsyncClient

os.environ.setdefault("HERMES_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("HERMES_JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("HERMES_RATE_LIMIT_PER_MINUTE", "1000")

from app.main import app, database  # noqa: E402
from app.db.base import Base  # noqa: E402


@pytest.fixture(scope="session")
def event_loop() -> AsyncIterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def prepare_database() -> AsyncIterator[None]:
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
