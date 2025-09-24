"""init

Revision ID: 0001
Revises:
Create Date: 2025-09-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# ревизия
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("role", sa.String, nullable=False),
    )

    op.create_table(
        "student_profile",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tutor_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("level", sa.Integer, nullable=False, server_default="1"),
    )

    op.create_table(
        "lesson",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id")),
        sa.Column("date", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("topic", sa.String, nullable=True),
    )

def downgrade() -> None:
    op.drop_table("lesson")
    op.drop_table("student_profile")
    op.drop_table("user")
