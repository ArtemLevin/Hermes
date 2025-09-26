from __future__ import annotations
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from deps import get_db
from models import Assignment, Submission, Student, ErrorHotspot

router = APIRouter()

# ===== Helpers =====
def _calc_tempo(db: Session, student_id: int, days: int = 30) -> dict:
    since = datetime.utcnow() - timedelta(days=days)
    subs = db.execute(
        select(Submission).join(Assignment).where(
            Assignment.student_id == student_id,
            Submission.completed_at >= since,
        )
    ).scalars().all()
    freq = len(subs) / days
    avg_time = None  # TODO: если будут данные "time_spent"
    return {"frequency_per_day": freq, "avg_time": avg_time}

def _forecast_exam(db: Session, student_id: int) -> dict:
    # простая модель: уровень ~ кол-во сабмитов * 2
    subs = db.execute(
        select(func.count(Submission.id))
        .join(Assignment)
        .where(Assignment.student_id == student_id)
    ).scalar_one()
    predicted_score = min(100, 40 + subs * 2)
    return {"predicted_score": predicted_score, "subs": subs}

def _priority_score(db: Session, student: Student) -> float:
    # простой эвристический скор: просрочки + hotspots + редкие сабмиты
    late_count = db.scalar(
        select(func.count(Assignment.id)).where(
            Assignment.student_id == student.id, Assignment.status == "late"
        )
    )
    hotspots = db.execute(
        select(func.sum(ErrorHotspot.heat)).where(ErrorHotspot.student_id == student.id)
    ).scalar_one() or 0
    tempo = _calc_tempo(db, student.id)
    score = late_count * 2 + hotspots - tempo["frequency_per_day"] * 10
    return score

# ===== Endpoints =====

@router.get("/tempo")
def tempo(
    student_id: int = Query(...),
    days: int = Query(30),
    db: Session = Depends(get_db),
):
    return _calc_tempo(db, student_id, days)

@router.get("/exam-forecast")
def exam_forecast(student_id: int = Query(...), db: Session = Depends(get_db)):
    return _forecast_exam(db, student_id)

@router.get("/priority-radar")
def priority_radar(db: Session = Depends(get_db)):
    students = db.execute(select(Student)).scalars().all()
    items = []
    for s in students:
        score = _priority_score(db, s)
        items.append(
            {"student_id": s.id, "name": s.name, "score": score, "level": s.level}
        )
    # сортировка по score
    items.sort(key=lambda x: x["score"], reverse=True)
    return {"items": items}
