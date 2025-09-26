"""Schemas for student endpoints."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StudentBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    level: int = Field(default=1, ge=1)
    progress_points: int = Field(default=0, ge=0)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    level: int | None = Field(default=None, ge=1)
    progress_points: int | None = Field(default=None, ge=0)


class StudentOut(StudentBase):
    id: int
    tutor_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
