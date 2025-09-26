"""Business logic for student management."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Student
from app.schemas import StudentCreate, StudentOut, StudentUpdate


class StudentNotFoundError(Exception):
    pass


class StudentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_students(self, tutor_id: int, skip: int = 0, limit: int = 100) -> list[StudentOut]:
        stmt = (
            select(Student)
            .where(Student.tutor_id == tutor_id)
            .offset(skip)
            .limit(limit)
            .order_by(Student.id)
        )
        result = await self.session.execute(stmt)
        students = result.scalars().all()
        return [StudentOut.model_validate(student) for student in students]

    async def get_student(self, tutor_id: int, student_id: int) -> Student:
        stmt = select(Student).where(Student.id == student_id, Student.tutor_id == tutor_id)
        result = await self.session.execute(stmt)
        student = result.scalar_one_or_none()
        if student is None:
            raise StudentNotFoundError
        return student

    async def create_student(self, tutor_id: int, payload: StudentCreate) -> StudentOut:
        student = Student(tutor_id=tutor_id, **payload.model_dump())
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return StudentOut.model_validate(student)

    async def update_student(self, tutor_id: int, student_id: int, payload: StudentUpdate) -> StudentOut:
        student = await self.get_student(tutor_id, student_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(student, field, value)
        await self.session.commit()
        await self.session.refresh(student)
        return StudentOut.model_validate(student)

    async def delete_student(self, tutor_id: int, student_id: int) -> None:
        student = await self.get_student(tutor_id, student_id)
        await self.session.delete(student)
        await self.session.commit()
