"""Security utilities such as password hashing and JWT creation."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(settings: Settings, subject: str) -> tuple[str, int]:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt, int(expires_delta.total_seconds())


def decode_access_token(settings: Settings, token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


class InvalidTokenError(Exception):
    pass


def verify_token(settings: Settings, token: str) -> str:
    try:
        payload = decode_access_token(settings, token)
        subject: str = payload.get("sub")  # type: ignore[assignment]
        if subject is None:
            raise InvalidTokenError("Token missing subject")
        return subject
    except JWTError as exc:  # pragma: no cover - jose specific
        raise InvalidTokenError(str(exc)) from exc
