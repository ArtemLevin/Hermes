from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from deps import get_db
from models import Base, Student, AvatarTheme
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, Date, DateTime, ForeignKey

router = APIRouter()

# --- Локальная ORM-модель для таблицы student_bio (создана миграцией 0003) ---
class StudentBio(Base):
    __tablename__ = "student_bio"
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("student_profile.id", ondelete="CASCADE"), primary_key=True
    )
    started_at: Mapped[date | None] = mapped_column(Date, default=None)
    goals: Mapped[str | None] = mapped_column(Text, default=None)
    strengths: Mapped[str | None] = mapped_column(Text, default=None)
    weaknesses: Mapped[str | None] = mapped_column(Text, default=None)
    notes: Mapped[str | None] = mapped_column(Text, default=None)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# --- Schemas ---
class StudentBioIn(BaseModel):
    started_at: date | None = None
    goals: str | None = None
    strengths: str | None = None
    weaknesses: str | None = None
    notes: str | None = None

class StudentBioOut(StudentBioIn):
    student_id: int
    updated_at: datetime

class AvatarSetIn(BaseModel):
    avatar_theme_code: str  # "warrior" | "mage" | "explorer" (см. сиды)

# --- Endpoints ---
@router.get("/students/{student_id}/bio", response_model=StudentBioOut)
def get_bio(student_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    # ensure student exists
    if not db.get(Student, student_id):
        raise HTTPException(404, "Student not found")

    bio = db.get(StudentBio, student_id)
    if not bio:
        # лениво создаём пустую запись при первом запросе
        bio = StudentBio(student_id=student_id)
        db.add(bio)
        db.commit()
        db.refresh(bio)
    return StudentBioOut(
        student_id=bio.student_id,
        started_at=bio.started_at,
        goals=bio.goals,
        strengths=bio.strengths,
        weaknesses=bio.weaknesses,
        notes=bio.notes,
        updated_at=bio.updated_at,
    )

@router.put("/students/{student_id}/bio", response_model=StudentBioOut)
def upsert_bio(
    student_id: int,
    payload: StudentBioIn,
    db: Session = Depends(get_db),
):
    if not db.get(Student, student_id):
        raise HTTPException(404, "Student not found")

    bio = db.get(StudentBio, student_id)
    if not bio:
        bio = StudentBio(student_id=student_id)
        db.add(bio)

    bio.started_at = payload.started_at
    bio.goals = payload.goals
    bio.strengths = payload.strengths
    bio.weaknesses = payload.weaknesses
    bio.notes = payload.notes
    bio.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(bio)
    return StudentBioOut(
        student_id=bio.student_id,
        started_at=bio.started_at,
        goals=bio.goals,
        strengths=bio.strengths,
        weaknesses=bio.weaknesses,
        notes=bio.notes,
        updated_at=bio.updated_at,
    )

@router.put("/students/{student_id}/avatar")
def set_avatar(
    student_id: int,
    payload: AvatarSetIn,
    db: Session = Depends(get_db),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    theme = db.scalar(select(AvatarTheme).where(AvatarTheme.code == payload.avatar_theme_code))
    if not theme:
        raise HTTPException(404, "Avatar theme not found")

    student.avatar_theme_id = theme.id
    db.commit()
    return {"student_id": student_id, "avatar_theme_id": theme.id, "code": theme.code}
