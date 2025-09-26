from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from deps import get_db
from models import Topic, ErrorHotspot

router = APIRouter()

# ===== Schemas =====
class TopicIn(BaseModel):
    name: str

class TopicOut(BaseModel):
    id: int
    name: str

class HeatIn(BaseModel):
    topic_id: int
    delta: int  # насколько увеличить "heat"

# ===== Endpoints =====
@router.get("")
def list_topics(db: Session = Depends(get_db)):
    rows = db.execute(select(Topic).order_by(Topic.name)).scalars().all()
    return [{"id": t.id, "name": t.name} for t in rows]

@router.post("")
def create_topic(payload: TopicIn, db: Session = Depends(get_db)):
    t = Topic(name=payload.name)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "name": t.name}

@router.get("/heatmap")
def student_heatmap(student_id: int = Query(...), db: Session = Depends(get_db)):
    rows = db.execute(
        select(ErrorHotspot).where(ErrorHotspot.student_id == student_id)
    ).scalars().all()
    return [
        {"topic_id": h.topic_id, "heat": h.heat, "updated_at": h.updated_at.isoformat()}
        for h in rows
    ]

@router.post("/heatmap")
def adjust_heat(student_id: int, payload: HeatIn, db: Session = Depends(get_db)):
    h = db.scalar(
        select(ErrorHotspot).where(
            ErrorHotspot.student_id == student_id, ErrorHotspot.topic_id == payload.topic_id
        )
    )
    if not h:
        h = ErrorHotspot(student_id=student_id, topic_id=payload.topic_id, heat=0)
        db.add(h)
    h.heat = max(0, (h.heat or 0) + payload.delta)
    db.commit()
    db.refresh(h)
    return {"topic_id": h.topic_id, "heat": h.heat}
