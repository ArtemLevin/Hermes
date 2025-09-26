# api/routers/student_bio.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from api.deps import get_db
from api.models import Student, StudentBio
from api.schemas import StudentBioIn, StudentBioOut, AvatarSetIn
from api.security import get_current_user

router = APIRouter()

@router.get("/students/{student_id}/bio", response_model=StudentBioOut)
def get_bio(student_id: int = Path(..., ge=1), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Ensure student belongs to current user
    student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")
    bio = db.query(StudentBio).filter(StudentBio.student_id == student_id).first()
    if not bio:
        # Create empty bio if it doesn't exist
        bio = StudentBio(student_id=student_id)
        db.add(bio)
        db.commit()
        db.refresh(bio)
    return bio

@router.put("/students/{student_id}/bio", response_model=StudentBioOut)
def update_bio(
    student_id: int,
    bio_data: StudentBioIn,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Ensure student belongs to current user
    student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")
    bio = db.query(StudentBio).filter(StudentBio.student_id == student_id).first()
    if not bio:
        bio = StudentBio(student_id=student_id, **bio_data.dict(exclude_unset=True))
        db.add(bio)
    else:
        for key, value in bio_data.dict(exclude_unset=True).items():
            setattr(bio, key, value)
    bio.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bio)
    return bio

# Avatar endpoint is not fully implemented in the original, placeholder added
@router.post("/students/{student_id}/avatar")
def set_avatar(student_id: int, avatar_data: AvatarSetIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Validate student ownership
    student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")
    # In a real app, you would link the avatar theme code to the student
    # This is a placeholder logic
    from api.models import AvatarTheme
    avatar_theme = db.query(AvatarTheme).filter(AvatarTheme.code == avatar_data.avatar_theme_code).first()
    if not avatar_theme:
        raise HTTPException(status_code=404, detail="Avatar theme not found")
    # Link student and avatar_theme (e.g., via a new column in Student or a separate table)
    # Assuming a column `avatar_theme_code` in Student table for simplicity
    student.avatar_theme_code = avatar_data.avatar_theme_code
    db.commit()
    return {"message": "Avatar set successfully"}