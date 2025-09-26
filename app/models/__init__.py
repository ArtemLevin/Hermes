"""Model registry to ease imports."""
from .user import User
from .student import Student
from .assignment import Assignment
from .idempotency import IdempotencyKey

__all__ = ["User", "Student", "Assignment", "IdempotencyKey"]
