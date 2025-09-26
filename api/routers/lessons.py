from __future__ import annotations
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from deps import get_db, pagination, Page
from models import Lesson, Student
from jobs import enqueue_lesson_reminder
from audit import audit_event

router = APIRouter()

# ==== Schemas ====
class LessonCreateIn(BaseModel):
    student_id: int
    date: datetime
    topic: str

class LessonOut(BaseModel):
    id: int
    student_id: int
    date: datetime
    topic: str

# ==== Endpoints ====
@router.get("")
def list_lessons(
    db: Session = Depends(get_db),
    page: Page = Depends(pagination),
    student_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
):
    stmt = select(Lesson)
    if student_id:
        stmt = stmt.where(Lesson.student_id == student_id)
    if date_from:
        stmt = stmt.where(Lesson.date >= date_from)
    if date_to:
        stmt = stmt.where(Lesson.date <= date_to)
    rows = db.execute(stmt.order_by(Lesson.date.asc())).scalars().all()

    total = len(rows)
    start = (page.page - 1) * page.size
    items = rows[start : start + page.size]

    return {
        "total": total,
        "items": [
            {"id": l.id, "student_id": l.student_id, "date": l.date, "topic": l.topic}
            for l in items
        ],
    }

@router.post("", response_model=LessonOut)
def create_lesson(payload: LessonCreateIn, db: Session = Depends(get_db)):
    # validate student
    if not db.get(Student, payload.student_id):
        raise HTTPException(404, "Student not found")

    l = Lesson(student_id=payload.student_id, date=payload.date, topic=payload.topic)
    db.add(l)
    db.commit()
    db.refresh(l)

    # шедулим напоминание «урок завтра» (email-заглушка)
    enqueue_lesson_reminder(
        student_email=f"student+{payload.student_id}@example.com",
        lesson_id=l.id,
        start_at=l.date,
    )

    audit_event("create_lesson", lesson_id=l.id, student_id=l.student_id, date=l.date.isoformat())
    return LessonOut(id=l.id, student_id=l.student_id, date=l.date, topic=l.topic)
