# scripts/seed.py
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base, User, Student
from api.security import hash_password

# Adjust path to import from api package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).filter(User.email == "tutor@example.com").first():
            print("Seed data already exists.")
            return

        # Create Tutor
        tutor = User(
            email="tutor@example.com",
            password_hash=hash_password("password123"),
            role="tutor"
        )
        db.add(tutor)
        db.commit()
        db.refresh(tutor)

        # Create Students
        student1 = Student(name="Alice Johnson", tutor_id=tutor.id)
        student2 = Student(name="Bob Smith", tutor_id=tutor.id)
        student3 = Student(name="Charlie Brown", tutor_id=tutor.id)

        db.add_all([student1, student2, student3])
        db.commit()

        print("Seed data created successfully.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()