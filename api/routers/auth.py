from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import User
from deps import get_db
from security import hash_password, verify_password, make_token

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    role: str = "tutor"

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
    email: EmailStr
    password: str

@router.post("/login")
def login(p: LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.email == p.email))
    if not u or not verify_password(p.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"token": make_token(u.id, u.role), "role": u.role}
