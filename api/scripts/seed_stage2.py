# scripts/seed_stage2.py
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base, Topic, AvatarTheme, Trophy, Mem, Tournament, TournamentParticipant

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
        if db.query(Topic).filter(Topic.name == "Algebra").first():
            print("Stage 2 seed data already exists.")
            return

        # Create Topics
        topics = [
            Topic(name="Algebra"),
            Topic(name="Geometry"),
            Topic(name="Calculus"),
            Topic(name="Statistics"),
        ]
        db.add_all(topics)
        db.commit()

        # Create Avatar Themes
        avatar_themes = [
            AvatarTheme(code="warrior", label="Воин 🛡️"),
            AvatarTheme(code="mage", label="Маг 🪄"),
            AvatarTheme(code="explorer", label="Исследователь 🧭"),
        ]
        db.add_all(avatar_themes)
        db.commit()

        # Create Trophies
        trophies = [
            Trophy(name="First Steps", description="Completed first assignment"),
            Trophy(name="Perfect Score", description="Got 5 on an assignment"),
            Trophy(name="Week Streak", description="Completed assignments for 7 days straight"),
        ]
        db.add_all(trophies)
        db.commit()

        # Create Memes
        mems = [
            Mem(title="Math Meme 1", image_url="https://example.com/meme1.jpg"),
            Mem(title="Math Meme 2", image_url="https://example.com/meme2.jpg"),
        ]
        db.add_all(mems)
        db.commit()

        # Create Tournament
        tournament = Tournament(
            name="Fall Math Challenge",
            description="A friendly competition for all students.",
            start_date=datetime.utcnow().date(),
            end_date=(datetime.utcnow() + timedelta(days=30)).date()
        )
        db.add(tournament)
        db.commit()

        print("Stage 2 seed data created successfully.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()