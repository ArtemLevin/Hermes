# api/routers/assignments.py
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db
from api.models import Assignment, Student, Submission
from api.schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate, SubmissionCreate, SubmissionOut
from api.security import get_current_user

router = APIRouter()

def _reward_points(reward_type: str) -> int:
    """Calculate points based on reward type."""
    if reward_type == "xp":
        return 10
    elif reward_type == "trophy":
        return 50
    elif reward_type == "mem":
        return 20
    else:
        return 10 # default

@router.get("/", response_model=List[AssignmentOut])
def get_assignments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Only return assignments for students associated with the current tutor
    assignments = db.query(Assignment).join(Student).filter(Student.tutor_id == current_user.id).offset(skip).limit(limit).all()
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentOut)
def get_assignment(assignment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assignment = db.query(Assignment).join(Student).filter(Assignment.id == assignment_id, Student.tutor_id == current_user.id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or not accessible")
    return assignment

@router.post("/", response_model=AssignmentOut)
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Validate that the student belongs to the current user
    student = db.query(Student).filter(Student.id == assignment.student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student not found or not accessible")
    db_assignment = Assignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.put("/{assignment_id}", response_model=AssignmentOut)
def update_assignment(assignment_id: int, assignment: AssignmentUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_assignment = db.query(Assignment).join(Student).filter(Assignment.id == assignment_id, Student.tutor_id == current_user.id).first()
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or not accessible")
    for key, value in assignment.dict(exclude_unset=True).items():
        setattr(db_assignment, key, value)
    db_assignment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.post("/{assignment_id}/start")
def start_assignment(assignment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assignment = db.query(Assignment).join(Student).filter(Assignment.id == assignment_id, Student.tutor_id == current_user.id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or not accessible")
    if assignment.status == "done":
        raise HTTPException(status_code=400, detail="Assignment is already completed")
    assignment.status = "in_progress"
    db.commit()
    return {"status": assignment.status}

@router.post("/{assignment_id}/submit")
def submit_assignment(assignment_id: int, submission: SubmissionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assignment = db.query(Assignment).join(Student).filter(Assignment.id == assignment_id, Student.tutor_id == current_user.id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or not accessible")
    if assignment.status == "done":
        raise HTTPException(status_code=400, detail="Assignment is already submitted")

    # Create submission
    db_submission = Submission(assignment_id=assignment.id, **submission.dict())
    db.add(db_submission)

    # Update assignment status
    assignment.status = "done"
    db.commit()

    # Update student progress
    student = assignment.student
    gained = _reward_points(assignment.reward_type)
    student.progress_points = (student.progress_points or 0) + gained

    # Level up logic
    while student.progress_points >= 100:
        student.level += 1
        student.progress_points -= 100

    db.commit()
    return {"status": assignment.status, "gained_points": gained, "level": student.level}