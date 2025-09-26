from datetime import datetime, timedelta
from sqlalchemy import select
from deps import SessionLocal
from models import (
    Topic, AvatarTheme, Mem, Tournament, TournamentParticipant,
    Student, Assignment
)

def upsert_topic(db, name: str):
    t = db.scalar(select(Topic).where(Topic.name == name))
    if not t:
        t = Topic(name=name)
        db.add(t)
        db.flush()
    return t

def upsert_avatar(db, code: str, icon: str):
    a = db.scalar(select(AvatarTheme).where(AvatarTheme.code == code))
    if not a:
        a = AvatarTheme(code=code, icon=icon)
        db.add(a)
        db.flush()
    return a

def run():
    with SessionLocal() as db:
        # --- Темы ---
        topics = ["Алгебра", "Геометрия", "Интегралы", "Сочинение", "Физика: кинематика"]
        tmap = {name: upsert_topic(db, name) for name in topics}

        # --- Аватары ---
        avatars = [
            ("warrior", "🛡️"),
            ("mage", "🪄"),
            ("explorer", "🧭"),
        ]
        amap = {code: upsert_avatar(db, code, icon) for code, icon in avatars}

        # Привяжем аватары студентам по порядку, если не задано
        students = db.execute(select(Student)).scalars().all()
        for i, s in enumerate(students):
            if not s.avatar_theme_id:
                s.avatar_theme_id = list(amap.values())[i % len(amap)].id

        # --- Мемы (общие) ---
        mems = [
            ("https://i.imgflip.com/30b1gx.jpg", "Кек, но делай ДЗ!"),
            ("https://i.imgflip.com/1bij.jpg", "Держись, у тебя получится!"),
        ]
        for url, cap in mems:
            if not db.scalar(select(Mem).where(Mem.url == url)):
                db.add(Mem(url=url, caption=cap))

        # --- Турнир ---
        tour = db.scalar(select(Tournament).where(Tournament.name == "Осенний Кубок"))
        if not tour:
            tour = Tournament(
                name="Осенний Кубок",
                level=1,
                start_at=datetime.utcnow(),
                end_at=datetime.utcnow() + timedelta(days=14),
            )
            db.add(tour)
            db.flush()
            # добавим участников из первых двух студентов
            for s in students[:2]:
                db.add(TournamentParticipant(tournament_id=tour.id, student_id=s.id, points=0))

        # --- Простейшие ДЗ по студентам (если пусто) ---
        for s in students:
            has_any = db.scalar(select(Assignment).where(Assignment.student_id == s.id))
            if not has_any:
                due = datetime.utcnow() + timedelta(days=3)
                a1 = Assignment(
                    student_id=s.id, status="new", title="Повторить алгебру",
                    reward_type="coin", due_at=due
                )
                a1.topics = [tmap["Алгебра"]]
                db.add(a1)

                a2 = Assignment(
                    student_id=s.id, status="new", title="Задачи по геометрии",
                    reward_type="badge", due_at=due + timedelta(days=1)
                )
                a2.topics = [tmap["Геометрия"]]
                db.add(a2)

        db.commit()
    print("Stage2 seed done: topics, avatars, mems, tournament, sample assignments.")

if __name__ == "__main__":
    run()
