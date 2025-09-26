"""Dependency functions shared across routers."""
from __future__ import annotations

from typing import AsyncIterator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.models import User
from app.services.assignments import AssignmentService
from app.services.auth import AuthService, AuthenticationError
from app.services.idempotency import IdempotencyContext, build_context
from app.services.students import StudentService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_settings_dependency() -> Settings:
    return get_settings()


async def get_session_dependency() -> AsyncIterator[AsyncSession]:  # type: ignore[override]
    async with get_session() as session:
        yield session


async def get_auth_service(
    session: AsyncSession = Depends(get_session_dependency),
    settings: Settings = Depends(get_settings_dependency),
) -> AuthService:
    return AuthService(session=session, settings=settings)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        user = await auth_service.get_user_by_token(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return user


async def get_student_service(
    session: AsyncSession = Depends(get_session_dependency),
) -> StudentService:
    return StudentService(session=session)


async def get_assignment_service(
    session: AsyncSession = Depends(get_session_dependency),
) -> AssignmentService:
    return AssignmentService(session=session)


async def idempotency_dependency(
    request: Request,
    session: AsyncSession = Depends(get_session_dependency),
) -> IdempotencyContext:
    return await build_context(request, session)
