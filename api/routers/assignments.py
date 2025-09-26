from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from deps import get_db, pagination, Page
from models import Assignment, Submission, Topic, Student
from audit import audit_event

router = APIRouter()

# ====== Schemas ======
class AssignmentCreateIn(BaseModel):
    student_id: int
    lesson_id: Optional[int] = None
    title: Optional[str] = None
    reward_type: Optional[str] = None  # "badge" | "coin" | "star"
    due_at: Optional[datetime] = None
    topic_ids: List[int] = []
    checklist: List[str] = []  # пока не сохраняем отдельно (MVP)

class AssignmentOut(BaseModel):
    id: int
    student_id: int
    lesson_id: Optional[int]
    status: str
    title: Optional[str]
    reward_type: Optional[str]
    due_at: Optional[datetime]
    topic_ids: List[int]

class SubmissionIn(BaseModel):
    artifacts: List[str] = []
    grade: Optional[float] = None
    feedback: Optional[str] = None

# ====== Helpers ======
def _reward_points(kind: Optional[str]) -> int:
    if kind == "star":
        return 20
    if kind == "coin":
        return 15
    if kind == "badge":
        return 10
    return 8  # базовое

# ====== Endpoints ======
@router.get("")
def list_assignments(
    db: Session = Depends(get_db),
    page: Page = Depends(pagination),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
):
    stmt = select(Assignment)
    if student_id:
        stmt = stmt.where(Assignment.student_id == student_id)
    if status:
        stmt = stmt.where(Assignment.status == status)
    rows = db.execute(stmt.order_by(Assignment.created_at.desc())).scalars().all()

    # пагинация простым слайсом
    total = len(rows)
    start = (page.page - 1) * page.size
    items = rows[start : start + page.size]

    result = []
    for a in items:
        topic_ids = [t.id for t in a.topics] if a.topics else []
        result.append(
            {
                "id": a.id,
                "student_id": a.student_id,
                "lesson_id": a.lesson_id,
                "status": a.status,
                "title": a.title,
                "reward_type": a.reward_type,
                "due_at": a.due_at,
                "topic_ids": topic_ids,
            }
        )
    return {"total": total, "items": result}

@router.post("")
def create_assignment(payload: AssignmentCreateIn, db: Session = Depends(get_db)):
    # ensure student exists
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    a = Assignment(
        student_id=payload.student_id,
        lesson_id=payload.lesson_id,
        status="new",
        title=payload.title,
        reward_type=payload.reward_type,
        due_at=payload.due_at,
        created_at=datetime.utcnow(),
    )
    # bind topics
    if payload.topic_ids:
        topics = db.execute(select(Topic).where(Topic.id.in_(payload.topic_ids))).scalars().all()
        a.topics = topics

    db.add(a)
    db.commit()
    db.refresh(a)

    audit_event(
        "create_assignment",
        assignment_id=a.id,
        student_id=a.student_id,
        reward_type=a.reward_type,
        due_at=a.due_at.isoformat() if a.due_at else None,
    )
    return {"id": a.id}

@router.post("/{assignment_id}/start")
def start_assignment(assignment_id: int, db: Session = Depends(get_db)):
    a = db.get(Assignment, assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")
    if a.status not in ("new", "late"):
        raise HTTPException(400, "Assignment not in startable state")
    a.status = "in_progress"
    db.commit()
    audit_event("start_assignment", assignment_id=a.id, student_id=a.student_id)
    return {"status": a.status}

@router.post("/{assignment_id}/submit")
def submit_assignment(assignment_id: int, payload: SubmissionIn, db: Session = Depends(get_db)):
    a = db.get(Assignment, assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")

    # создаём сабмит
    sub = Submission(
        assignment_id=a.id,
        completed_at=datetime.utcnow().replace(tzinfo=None),
        grade=payload.grade,
        feedback=payload.feedback,
    )
    db.add(sub)

    # завершение задания
    a.status = "done"
    db.commit()

    # начисление очков за выполненное ДЗ
    student = db.get(Student, a.student_id)
    gained = _reward_points(a.reward_type)
    student.progress_points = (student.progress_points or 0) + gained
    # авто-повышение уровня: 100 очков = +1 уровень
    while student.progress_points >= 100:
        student.level += 1
        student.progress_points -= 100

    db.commit()

    audit_event(
        "submit_assignment",
        assignment_id=a.id,
        student_id=a.student_id,
        gained_points=gained,
        new_level=student.level,
        points_left=student.progress_points,
    )
    return {"status": a.status, "gained_points": gained, "level": student.level}

@router.post("/{assignment_id}/mark_late")
def mark_late(assignment_id: int, db: Session = Depends(get_db)):
    a = db.get(Assignment, assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")
    a.status = "late"
    db.commit()
    audit_event("mark_assignment_late", assignment_id=a.id, student_id=a.student_id)
    return {"status": a.status}
