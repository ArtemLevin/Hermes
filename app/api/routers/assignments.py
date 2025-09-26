"""Assignment endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_assignment_service,
    get_current_user,
    get_session_dependency,
    idempotency_dependency,
)
from app.models import User
from app.schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate
from app.services.assignments import AssignmentNotFoundError, AssignmentService
from app.services.idempotency import IdempotencyContext, persist_response
from app.services.students import StudentNotFoundError

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("/student/{student_id}", response_model=list[AssignmentOut])
async def list_assignments(
    student_id: int,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
) -> list[AssignmentOut]:
    try:
        return await service.list_assignments(current_user.id, student_id)
    except StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found") from exc


@router.post("/", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    payload: AssignmentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
    context: IdempotencyContext = Depends(idempotency_dependency),
    session: AsyncSession = Depends(get_session_dependency),
) -> JSONResponse | AssignmentOut:
    if context.has_cached_response:
        status_code, cached_body = context.response_payload()
        return JSONResponse(status_code=status_code, content=cached_body)
    try:
        assignment = await service.create_assignment(current_user.id, payload)
    except StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found") from exc

    key = request.headers.get("Idempotency-Key")
    await persist_response(session, key, context, status.HTTP_201_CREATED, assignment.model_dump())
    return assignment


@router.patch("/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(
    assignment_id: int,
    payload: AssignmentUpdate,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
) -> AssignmentOut:
    try:
        return await service.update_assignment(current_user.id, assignment_id, payload)
    except AssignmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found") from exc


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    service: AssignmentService = Depends(get_assignment_service),
) -> None:
    try:
        await service.delete_assignment(current_user.id, assignment_id)
    except AssignmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found") from exc
    return None
