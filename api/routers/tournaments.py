from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from deps import get_db
from models import Tournament, TournamentParticipant, Student

router = APIRouter()

# ===== Schemas =====
class TournamentCreateIn(BaseModel):
    name: str
    level: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None

class JoinIn(BaseModel):
    student_id: int

class ScoreIn(BaseModel):
    student_id: int
    points: int

# ===== Endpoints =====
@router.get("")
def list_tournaments(db: Session = Depends(get_db)):
    rows = db.execute(select(Tournament)).scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "level": t.level,
            "start_at": t.start_at,
            "end_at": t.end_at,
        }
        for t in rows
    ]

@router.post("")
def create_tournament(payload: TournamentCreateIn, db: Session = Depends(get_db)):
    t = Tournament(
        name=payload.name,
        level=payload.level,
        start_at=payload.start_at,
        end_at=payload.end_at,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id}

@router.post("/{tournament_id}/join")
def join_tournament(tournament_id: int, payload: JoinIn, db: Session = Depends(get_db)):
    t = db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    tp = TournamentParticipant(tournament_id=t.id, student_id=student.id, points=0)
    db.add(tp)
    db.commit()
    return {"status": "joined"}

@router.post("/{tournament_id}/score")
def add_score(tournament_id: int, payload: ScoreIn, db: Session = Depends(get_db)):
    tp = db.get(
        TournamentParticipant, {"tournament_id": tournament_id, "student_id": payload.student_id}
    )
    if not tp:
        raise HTTPException(404, "Not a participant")
    tp.points += payload.points
    db.commit()
    return {"points": tp.points}

@router.get("/{tournament_id}/leaderboard")
def leaderboard(tournament_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        select(TournamentParticipant).where(TournamentParticipant.tournament_id == tournament_id)
    ).scalars().all()
    result = [{"student_id": tp.student_id, "points": tp.points} for tp in rows]
    result.sort(key=lambda x: x["points"], reverse=True)
    return {"leaderboard": result}
