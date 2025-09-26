"""Authentication domain logic."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password, InvalidTokenError, verify_token
from app.models import User
from app.schemas import Token, UserCreate, UserOut


class AuthenticationError(Exception):
    pass


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    async def register_user(self, payload: UserCreate) -> UserOut:
        user = User(email=payload.email, hashed_password=hash_password(payload.password))
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise AuthenticationError("User already exists") from exc
        await self.session.refresh(user)
        return UserOut.model_validate(user)

    async def authenticate(self, email: str, password: str) -> Token:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")
        token, expires_in = create_access_token(self.settings, str(user.id))
        return Token(access_token=token, expires_in=expires_in)

    async def get_user_by_token(self, token: str) -> User:
        try:
            subject = verify_token(self.settings, token)
        except InvalidTokenError as exc:
            raise AuthenticationError(str(exc)) from exc

        stmt = select(User).where(User.id == int(subject))
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise AuthenticationError("User not found")
        return user
