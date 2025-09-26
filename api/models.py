from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer, String, Text, ForeignKey, DateTime, Numeric, Date
)

Base = declarative_base()

# ===== БАЗОВЫЕ МОДЕЛИ ЭТАПА 0 =====

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String)  # tutor | student | parent

class Student(Base):
    __tablename__ = "student_profile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tutor_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(String)
    level: Mapped[int] = mapped_column(Integer, default=1)
    # Этап 2:
    avatar_theme_id: Mapped[Optional[int]] = mapped_column(ForeignKey("avatar_theme.id"), default=None)
    progress_points: Mapped[int] = mapped_column(Integer, default=0)

    lessons: Mapped[List["Lesson"]] = relationship(back_populates="student", cascade="all,delete-orphan")
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="student", cascade="all,delete-orphan")
    trophies: Mapped[List["Trophy"]] = relationship(back_populates="student", cascade="all,delete-orphan")

class Lesson(Base):
    __tablename__ = "lesson"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profile.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    topic: Mapped[str] = mapped_column(String, default="")

    student: Mapped[Student] = relationship(back_populates="lessons")


# ===== ЭТАП 2: ДОП. СУЩНОСТИ (учебные) =====

class Topic(Base):
    __tablename__ = "topic"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

class AssignmentTopic(Base):
    __tablename__ = "assignment_topic"
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignment.id", ondelete="CASCADE"), primary_key=True
    )
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topic.id", ondelete="CASCADE"), primary_key=True
    )

class Assignment(Base):
    __tablename__ = "assignment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profile.id"))
    lesson_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lesson.id"), default=None)
    status: Mapped[str] = mapped_column(String)  # 'new'|'in_progress'|'done'|'late'
    title: Mapped[Optional[str]] = mapped_column(String, default=None)
    reward_type: Mapped[Optional[str]] = mapped_column(String, default=None)  # badge/coin/star
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped[Student] = relationship(back_populates="assignments")
    lesson: Mapped[Optional[Lesson]] = relationship()
    topics: Mapped[List[Topic]] = relationship(
        secondary="assignment_topic",
        lazy="selectin",
    )
    submissions: Mapped[List["Submission"]] = relationship(
        back_populates="assignment", cascade="all,delete-orphan"
    )

class Submission(Base):
    __tablename__ = "submission"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignment.id", ondelete="CASCADE"))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    grade: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), default=None)
    feedback: Mapped[Optional[str]] = mapped_column(Text, default=None)

    assignment: Mapped[Assignment] = relationship(back_populates="submissions")

class ErrorHotspot(Base):
    __tablename__ = "error_hotspot"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profile.id"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))
    heat: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AvatarTheme(Base):
    __tablename__ = "avatar_theme"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    icon: Mapped[str] = mapped_column(String)

class Trophy(Base):
    __tablename__ = "trophy"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profile.id"))
    name: Mapped[str] = mapped_column(String)
    reason: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped[Student] = relationship(back_populates="trophies")

class Mem(Base):
    __tablename__ = "mem"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("student_profile.id"), default=None)
    url: Mapped[str] = mapped_column(String)
    caption: Mapped[Optional[str]] = mapped_column(String, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Tournament(Base):
    __tablename__ = "tournament"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    level: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    start_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    end_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)

    participants: Mapped[List["TournamentParticipant"]] = relationship(
        back_populates="tournament", cascade="all,delete-orphan"
    )

class TournamentParticipant(Base):
    __tablename__ = "tournament_participant"
    tournament_id: Mapped[int] = mapped_column(
        ForeignKey("tournament.id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("student_profile.id", ondelete="CASCADE"), primary_key=True
    )
    points: Mapped[int] = mapped_column(Integer, default=0)

    tournament: Mapped[Tournament] = relationship(back_populates="participants")


# ===== ЭТАП 2: ФИНАНСЫ =====

class Invoice(Base):
    __tablename__ = "invoice"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profile.id"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String)  # draft|issued|paid|overdue|canceled
    due_date: Mapped[Optional[datetime]] = mapped_column(Date, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    notes: Mapped[Optional[str]] = mapped_column(Text, default=None)


class Payment(Base):
    __tablename__ = "payment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profile.id"))
    invoice_id: Mapped[Optional[int]] = mapped_column(ForeignKey("invoice.id"), default=None)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String)  # pending|paid|failed|refunded
    method: Mapped[Optional[str]] = mapped_column(String, default=None)  # cash|transfer|card
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
