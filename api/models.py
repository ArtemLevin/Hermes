from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from datetime import datetime

Base = declarative_base()

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

class Lesson(Base):
    __tablename__ = "lesson"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profile.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    topic: Mapped[str] = mapped_column(String, default="")
