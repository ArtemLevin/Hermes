from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.orm import Session

from deps import get_db, pagination, Page
from models import Mem

router = APIRouter()

class MemCreateIn(BaseModel):
    url: HttpUrl
    caption: str | None = None
    student_id: int | None = None

@router.get("")
def list_mems(
    db: Session = Depends(get_db),
    page: Page = Depends(pagination),
    student_id: int | None = Query(None),
):
    stmt = select(Mem).order_by(Mem.created_at.desc())
    if student_id:
        stmt = stmt.where(Mem.student_id == student_id)
    rows = db.execute(stmt).scalars().all()
    total = len(rows)
    start = (page.page - 1) * page.size
    items = rows[start : start + page.size]
    return {
        "total": total,
        "items": [{"id": m.id, "url": m.url, "caption": m.caption, "student_id": m.student_id} for m in items],
    }

@router.post("")
def create_mem(payload: MemCreateIn, db: Session = Depends(get_db)):
    m = Mem(url=str(payload.url), caption=payload.caption, student_id=payload.student_id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"id": m.id, "url": m.url, "caption": m.caption, "student_id": m.student_id}
