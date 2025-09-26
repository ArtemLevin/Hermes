"""Authentication API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service
from app.schemas import Token, UserCreate, UserOut
from app.services.auth import AuthService, AuthenticationError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, auth_service: AuthService = Depends(get_auth_service)) -> UserOut:
    try:
        return await auth_service.register_user(payload)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)) -> Token:
    try:
        return await auth_service.authenticate(form_data.username, form_data.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
