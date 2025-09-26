from datetime import datetime, timedelta
from random import choice

from sqlalchemy import select
from deps import SessionLocal
from models import Lesson, Student

TOPICS = [
    "Алгебра: уравнения",
    "Геометрия: треугольники",
    "Интегралы: вводная",
    "Физика: кинематика",
    "Русский: сочинение",
]

def run(days_back: int = 7, days_forward: int = 7, per_day: int = 2) -> None:
    """
    Создаёт уроки за прошедшие и ближайшие дни.
    - days_back: сколько дней назад
    - days_forward: сколько дней вперёд
    - per_day: сколько уроков в день (если есть студенты)
    """
    with SessionLocal() as db:
        students = db.execute(select(Student)).scalars().all()
        if not students:
            print("Нет студентов — запустите make seed сначала.")
            return

        start = datetime.utcnow() - timedelta(days=days_back)
        total = 0
        for i in range(days_back + days_forward + 1):
            day = start + timedelta(days=i)
            # равномерно расписать по студентам
            for k in range(per_day):
                s = students[(i + k) % len(students)]
                t = choice(TOPICS)
                # время в течение дня (10:00 + k*2 часа)
                dt = day.replace(hour=10 + k * 2, minute=0, second=0, microsecond=0)
                l = Lesson(student_id=s.id, date=dt, topic=t)
                db.add(l)
                total += 1
        db.commit()
        print(f"Создано уроков: {total}")

if __name__ == "__main__":
    run()
