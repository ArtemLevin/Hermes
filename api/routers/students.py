# api/routers/students.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db
from api.models import Student, User
from api.schemas import StudentCreate, StudentOut, StudentUpdate
from api.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[StudentOut])
def get_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Only return students associated with the current tutor
    students = db.query(Student).filter(Student.tutor_id == current_user.id).offset(skip).limit(limit).all()
    return students

@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")
    return student

@router.post("/", response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Ensure tutor_id matches the current user's ID
    db_student = Student(**student.dict(), tutor_id=current_user.id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.put("/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")
    for key, value in student.dict(exclude_unset=True).items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}