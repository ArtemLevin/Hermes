"""Schema exports."""
from .auth import Token, TokenPayload, UserCreate, UserOut
from .student import StudentCreate, StudentOut, StudentUpdate
from .assignment import AssignmentCreate, AssignmentOut, AssignmentUpdate

__all__ = [
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserOut",
    "StudentCreate",
    "StudentOut",
    "StudentUpdate",
    "AssignmentCreate",
    "AssignmentOut",
    "AssignmentUpdate",
]
