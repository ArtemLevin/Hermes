"""Persisted idempotency key helper."""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from typing import Any, Mapping

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IdempotencyKey


@dataclass
class IdempotencyContext:
    request_hash: str
    existing: IdempotencyKey | None

    @property
    def has_cached_response(self) -> bool:
        return self.existing is not None

    def response_payload(self) -> tuple[int, Mapping[str, Any]]:
        assert self.existing is not None
        payload = json.loads(self.existing.response_body)
        return self.existing.response_status, payload


async def build_context(request: Request, session: AsyncSession) -> IdempotencyContext:
    key = request.headers.get("Idempotency-Key")
    body_bytes = await request.body()
    body_hash = hashlib.sha256(body_bytes).hexdigest()
    request_hash = f"{request.method}:{request.url.path}:{body_hash}"

    if not key:
        return IdempotencyContext(request_hash=request_hash, existing=None)

    stmt = select(IdempotencyKey).where(IdempotencyKey.key == key)
    result = await session.execute(stmt)
    record = result.scalar_one_or_none()
    if record and record.request_hash != request_hash:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency key reuse with different payload")
    return IdempotencyContext(request_hash=request_hash, existing=record)


async def persist_response(
    session: AsyncSession,
    key: str | None,
    context: IdempotencyContext,
    status_code: int,
    payload: Mapping[str, Any],
) -> None:
    if key is None or context.existing is not None:
        return
    record = IdempotencyKey(
        key=key,
        request_hash=context.request_hash,
        response_status=status_code,
        response_body=json.dumps(payload, sort_keys=True),
    )
    session.add(record)
    await session.commit()
