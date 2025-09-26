# api/schemas.py
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, field_validator

# --- User ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: str = "tutor"

class UserOut(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Student ---
class StudentBase(BaseModel):
    name: str
    level: int = 1
    progress_points: int = 0

class StudentCreate(StudentBase):
    tutor_id: Optional[int] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    progress_points: Optional[int] = None

class StudentOut(StudentBase):
    id: int
    tutor_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Lesson ---
class LessonBase(BaseModel):
    student_id: int
    date: datetime
    topic: Optional[str] = None

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    date: Optional[datetime] = None
    topic: Optional[str] = None

class LessonOut(LessonBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Assignment ---
class AssignmentBase(BaseModel):
    student_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    reward_type: str = "xp"

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[str] = None

class AssignmentOut(AssignmentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Submission ---
class SubmissionBase(BaseModel):
    assignment_id: int
    grade: Optional[int] = None
    feedback: Optional[str] = None
    artifacts: Optional[str] = None # JSON string

class SubmissionCreate(SubmissionBase):
    completed_at: datetime

class SubmissionOut(SubmissionBase):
    id: int
    completed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# --- Topic ---
class TopicBase(BaseModel):
    name: str

class TopicCreate(TopicBase):
    pass

class TopicOut(TopicBase):
    id: int

    class Config:
        from_attributes = True

# --- Error Hotspot ---
class HeatmapUpdate(BaseModel):
    topic_id: int
    delta: int

class HeatmapOut(BaseModel):
    topic_id: int
    heat: int

    class Config:
        from_attributes = True

# --- Student Bio ---
class StudentBioIn(BaseModel):
    started_at: Optional[date] = None
    goals: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('goals', 'strengths', 'weaknesses', 'notes')
    def validate_text_length(cls, v):
        if v and len(v) > 1000:  # Example limit
            raise ValueError('Field must not exceed 1000 characters')
        return v

class StudentBioOut(StudentBioIn):
    student_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Avatar ---
class AvatarSetIn(BaseModel):
    avatar_theme_code: str # "warrior", "mage", "explorer"

# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None