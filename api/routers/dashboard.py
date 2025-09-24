from pathlib import Path
import sys

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

if not (__package__ or "").startswith("api."):
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from deps import get_db
    from models import Lesson, Student
else:  # pragma: no cover - ветка для запуска как пакет
    from ..deps import get_db
    from ..models import Lesson, Student

router = APIRouter()

@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    # Минимальные метрики для дашборда
    students_count = db.execute(select(func.count(Student.id))).scalar_one()
    lessons_count = db.execute(select(func.count(Lesson.id))).scalar_one()

    # Простейшая имитация серии прогресса (оставим статик в MVP)
    progress_series = [
        {"date": "2025-09-01", "value": 60},
        {"date": "2025-09-08", "value": 65},
        {"date": "2025-09-15", "value": 70},
    ]

    engagement_temp = 0.72  # placeholder до этапа аналитики

    alerts: list[dict] = []  # сюда позже попадут просрочки/платежи

    return {
        "students_count": students_count,
        "lessons_count": lessons_count,
        "progress_series": progress_series,
        "engagement_temp": engagement_temp,
        "alerts": alerts,
    }
