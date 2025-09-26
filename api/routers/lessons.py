# api/routers/lessons.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db
from api.models import Lesson, Student
from api.schemas import LessonCreate, LessonOut, LessonUpdate
from api.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[LessonOut])
def get_lessons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Only return lessons for students associated with the current tutor
    lessons = db.query(Lesson).join(Student).filter(Student.tutor_id == current_user.id).offset(skip).limit(limit).all()
    return lessons

@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    lesson = db.query(Lesson).join(Student).filter(Lesson.id == lesson_id, Student.tutor_id == current_user.id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found or not accessible")
    return lesson

@router.post("/", response_model=LessonOut)
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Validate that the student belongs to the current user
    student = db.query(Student).filter(Student.id == lesson.student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student not found or not accessible")
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@router.put("/{lesson_id}", response_model=LessonOut)
def update_lesson(lesson_id: int, lesson: LessonUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_lesson = db.query(Lesson).join(Student).filter(Lesson.id == lesson_id, Student.tutor_id == current_user.id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found or not accessible")
    for key, value in lesson.dict(exclude_unset=True).items():
        setattr(db_lesson, key, value)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@router.delete("/{lesson_id}")
def delete_lesson(lesson_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_lesson = db.query(Lesson).join(Student).filter(Lesson.id == lesson_id, Student.tutor_id == current_user.id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found or not accessible")
    db.delete(db_lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"}