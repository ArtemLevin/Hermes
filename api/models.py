# api/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text, Float, Date
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Association table for student-trophies
student_trophies = Table(
    'student_trophies',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('student_profile.id'), primary_key=True),
    Column('trophy_id', Integer, ForeignKey('trophy.id'), primary_key=True)
)

# Association table for student-memes
student_memes = Table(
    'student_memes',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('student_profile.id'), primary_key=True),
    Column('mem_id', Integer, ForeignKey('mem.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="tutor", nullable=False) # tutor, student, parent
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    students = relationship("Student", back_populates="tutor")

class Student(Base):
    __tablename__ = "student_profile"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    progress_points = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Foreign key to User (tutor)
    tutor_id = Column(Integer, ForeignKey("user.id"))
    tutor = relationship("User", back_populates="students")

    # Relationships
    lessons = relationship("Lesson", back_populates="student")
    assignments = relationship("Assignment", back_populates="student")
    trophies = relationship("Trophy", secondary=student_trophies, back_populates="students")
    memes = relationship("Mem", secondary=student_memes, back_populates="students")
    payments = relationship("Payment", back_populates="student")
    invoices = relationship("Invoice", back_populates="student")
    bio = relationship("StudentBio", back_populates="student", uselist=False, cascade="all, delete-orphan")
    error_hotspots = relationship("ErrorHotspot", back_populates="student")

class Lesson(Base):
    __tablename__ = "lesson"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    date = Column(DateTime, nullable=False) # Includes time
    topic = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="lessons")

class Assignment(Base):
    __tablename__ = "assignment"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending", nullable=False) # pending, in_progress, done, late
    reward_type = Column(String, default="xp", nullable=False) # xp, trophy, mem
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submission"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)
    completed_at = Column(DateTime, nullable=False)
    grade = Column(Integer, nullable=True) # e.g., 1-5
    feedback = Column(Text, nullable=True)
    artifacts = Column(Text, nullable=True) # JSON string for file paths, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    assignment = relationship("Assignment", back_populates="submissions")

class Trophy(Base):
    __tablename__ = "trophy"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True) # e.g., emoji or path to image
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", secondary=student_trophies, back_populates="trophies")

class Mem(Base):
    __tablename__ = "mem"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=False) # URL or path to image
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", secondary=student_memes, back_populates="memes")

class Tournament(Base):
    __tablename__ = "tournament"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship("Student", secondary="tournament_participants")

class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    tournament_id = Column(Integer, ForeignKey("tournament.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), primary_key=True)
    score = Column(Float, default=0.0, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

class Topic(Base):
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # e.g., "Algebra", "Geometry"
    created_at = Column(DateTime, default=datetime.utcnow)

    error_hotspots = relationship("ErrorHotspot", back_populates="topic")

class ErrorHotspot(Base):
    __tablename__ = "error_hotspot"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topic.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    heat = Column(Integer, default=0, nullable=False) # A measure of difficulty/error frequency
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    topic = relationship("Topic", back_populates="error_hotspots")
    student = relationship("Student", back_populates="error_hotspots")

class AvatarTheme(Base):
    __tablename__ = "avatar_theme"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False) # e.g., "warrior", "mage"
    label = Column(String, nullable=False) # e.g., "Воин 🛡️"
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentBio(Base):
    __tablename__ = "student_bio"

    student_id = Column(Integer, ForeignKey("student_profile.id", ondelete="CASCADE"), primary_key=True)
    started_at = Column(Date, nullable=True)
    goals = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="bio")

class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="pending", nullable=False) # pending, paid, overdue
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="invoices")

class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profile.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    method = Column(String, default="cash", nullable=False) # cash, card, online
    status = Column(String, default="completed", nullable=False) # completed, failed, pending
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=True) # Link to invoice if applicable
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="payments")