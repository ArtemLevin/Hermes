"""Endpoints for working with students."""

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

if not (__package__ or "").startswith("api."):
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from deps import Page, get_db, pagination
    from models import Student
else:  # pragma: no cover - ветка для запуска как пакет
    from ..deps import Page, get_db, pagination
    from ..models import Student

router = APIRouter()

@router.get("")
def list_students(
    response: Response,
    q: str | None = None,
    page: Page = Depends(pagination),
    db: Session = Depends(get_db),
):
    filters = []
    if q:
        filters.append(Student.name.ilike(f"%{q.strip()}%"))

    total_stmt = select(func.count()).select_from(Student)
    if filters:
        total_stmt = total_stmt.where(*filters)
    total = db.scalar(total_stmt) or 0
    response.headers["X-Total-Count"] = str(total)

    start = (page.page - 1) * page.size
    items_stmt = (
        select(Student)
        .where(*filters)
        .order_by(Student.id)
        .offset(start)
        .limit(page.size)
    )
    students = db.execute(items_stmt).scalars().all()
    return [{"id": s.id, "name": s.name, "level": s.level} for s in students]
