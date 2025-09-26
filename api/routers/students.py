from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from deps import get_db, pagination, Page
from models import Student
from audit import audit_event

router = APIRouter()

class StudentCreateIn(BaseModel):
    name: str
    tutor_id: int
    level: int = 1

@router.get("")
def list_students(
    response: Response,
    q: str | None = None,
    page: Page = Depends(pagination),
    db: Session = Depends(get_db),
):
    stmt = select(Student)
    if q:
        stmt = stmt.where(Student.name.ilike(f"%{q}%"))
    all_students = db.execute(stmt).scalars().all()
    response.headers["X-Total-Count"] = str(len(all_students))
    start = (page.page - 1) * page.size
    items = [
        {"id": s.id, "name": s.name, "level": s.level}
        for s in all_students[start : start + page.size]
    ]
    return items

@router.post("")
def create_student(payload: StudentCreateIn, db: Session = Depends(get_db)):
    # простой дубль-чек по имени в рамках одного тьютора
    exists = db.scalar(
        select(Student).where(
            Student.tutor_id == payload.tutor_id,
            Student.name == payload.name,
        )
    )
    if exists:
        raise HTTPException(status_code=400, detail="Student already exists")

    s = Student(name=payload.name, tutor_id=payload.tutor_id, level=payload.level)
    db.add(s)
    db.commit()
    db.refresh(s)

    # аудит-событие
    audit_event(
        "create_student",
        student_id=s.id,
        tutor_id=s.tutor_id,
        name=s.name,
        level=s.level,
    )

    return {"id": s.id, "name": s.name, "level": s.level}
