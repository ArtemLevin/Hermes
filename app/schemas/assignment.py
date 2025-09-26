"""Schemas for assignments."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AssignmentBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: str = Field(default="pending")
    due_date: datetime | None = None


class AssignmentCreate(AssignmentBase):
    student_id: int


class AssignmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None)
    due_date: datetime | None = None


class AssignmentOut(AssignmentBase):
    id: int
    student_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
