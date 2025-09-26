"""Student endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_user,
    get_session_dependency,
    get_student_service,
    idempotency_dependency,
)
from app.models import User
from app.schemas import StudentCreate, StudentOut, StudentUpdate
from app.services.idempotency import IdempotencyContext, persist_response
from app.services.students import StudentNotFoundError, StudentService

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=list[StudentOut])
async def list_students(
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
    skip: int = 0,
    limit: int = 100,
) -> list[StudentOut]:
    return await service.list_students(current_user.id, skip=skip, limit=limit)


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> StudentOut:
    try:
        student = await service.get_student(current_user.id, student_id)
    except StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found") from exc
    return StudentOut.model_validate(student)


@router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
    context: IdempotencyContext = Depends(idempotency_dependency),
    session: AsyncSession = Depends(get_session_dependency),
) -> JSONResponse | StudentOut:
    if context.has_cached_response:
        status_code, cached_body = context.response_payload()
        return JSONResponse(status_code=status_code, content=cached_body)

    student = await service.create_student(current_user.id, payload)
    key = request.headers.get("Idempotency-Key")
    await persist_response(session, key, context, status.HTTP_201_CREATED, student.model_dump())
    return student


@router.patch("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: int,
    payload: StudentUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> StudentOut:
    try:
        return await service.update_student(current_user.id, student_id, payload)
    except StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found") from exc


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> None:
    try:
        await service.delete_student(current_user.id, student_id)
    except StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found") from exc
    return None
