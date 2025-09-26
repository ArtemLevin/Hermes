"""Assignment related business logic."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assignment
from app.schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate
from .students import StudentNotFoundError, StudentService


class AssignmentNotFoundError(Exception):
    pass


class AssignmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.student_service = StudentService(session)

    async def list_assignments(self, tutor_id: int, student_id: int) -> list[AssignmentOut]:
        await self.student_service.get_student(tutor_id, student_id)
        stmt = select(Assignment).where(Assignment.student_id == student_id).order_by(Assignment.id)
        result = await self.session.execute(stmt)
        assignments = result.scalars().all()
        return [AssignmentOut.model_validate(item) for item in assignments]

    async def create_assignment(self, tutor_id: int, payload: AssignmentCreate) -> AssignmentOut:
        await self.student_service.get_student(tutor_id, payload.student_id)
        assignment = Assignment(**payload.model_dump())
        self.session.add(assignment)
        await self.session.commit()
        await self.session.refresh(assignment)
        return AssignmentOut.model_validate(assignment)

    async def update_assignment(self, tutor_id: int, assignment_id: int, payload: AssignmentUpdate) -> AssignmentOut:
        assignment = await self.get_assignment_for_tutor(tutor_id, assignment_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(assignment, field, value)
        await self.session.commit()
        await self.session.refresh(assignment)
        return AssignmentOut.model_validate(assignment)

    async def delete_assignment(self, tutor_id: int, assignment_id: int) -> None:
        assignment = await self.get_assignment_for_tutor(tutor_id, assignment_id)
        await self.session.delete(assignment)
        await self.session.commit()

    async def get_assignment_for_tutor(self, tutor_id: int, assignment_id: int) -> Assignment:
        stmt = (
            select(Assignment)
            .join(Assignment.student)
            .where(Assignment.id == assignment_id, Assignment.student.has(tutor_id=tutor_id))
        )
        result = await self.session.execute(stmt)
        assignment = result.scalar_one_or_none()
        if assignment is None:
            raise AssignmentNotFoundError
        return assignment
