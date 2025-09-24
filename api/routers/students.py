from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from deps import get_db, pagination, Page
from models import Student

router = APIRouter()

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
