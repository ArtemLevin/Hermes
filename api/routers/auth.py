"""Authentication and authorisation endpoints."""

import re
import sys
from pathlib import Path
from typing import ClassVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

if not (__package__ or "").startswith("api."):
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from deps import get_db
    from models import User
    from security import hash_password, make_token, verify_password
else:  # pragma: no cover - ветка для запуска как пакет
    from ..deps import get_db
    from ..models import User
    from ..security import hash_password, make_token, verify_password

router = APIRouter()

class RegisterIn(BaseModel):
    email: str
    password: str
    role: str = "tutor"

    _EMAIL_RE: ClassVar[re.Pattern[str]] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not cls._EMAIL_RE.match(value):  # pragma: no cover - простая валидация
            raise ValueError("invalid email format")
        return value.lower()

@router.post("/register")
def register(p: RegisterIn, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == p.email)):
        raise HTTPException(400, "Email already exists")
    u = User(email=p.email, password_hash=hash_password(p.password), role=p.role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"id": u.id, "email": u.email}

class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        return value.lower()

@router.post("/login")
def login(p: LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.email == p.email))
    if not u or not verify_password(p.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"token": make_token(u.id, u.role), "role": u.role}
