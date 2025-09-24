from sqlalchemy import select
from deps import SessionLocal
from models import User, Student
from security import hash_password

def run():
    with SessionLocal() as db:
        tutor = db.scalar(select(User).where(User.email == "tutor@example.com"))
        if not tutor:
            tutor = User(
                email="tutor@example.com",
                password_hash=hash_password("tutor"),
                role="tutor",
            )
            db.add(tutor)
            db.commit()
            db.refresh(tutor)

        # Добавляем трёх учеников
        names = ["Лев", "Аня", "Марк"]
        for i, n in enumerate(names, start=1):
            exists = db.scalar(select(Student).where(Student.name == n))
            if not exists:
                s = Student(name=n, tutor_id=tutor.id, level=i)
                db.add(s)

        db.commit()
    print("Seed done. Login: tutor@example.com / tutor")

if __name__ == "__main__":
    run()
