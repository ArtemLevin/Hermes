"""stage2 add student_bio

Revision ID: 0003_student_bio
Revises: 0002_stage2
Create Date: 2025-09-26 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# ревизия
revision = "0003_student_bio"
down_revision = "0002_stage2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_bio",
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("started_at", sa.Date, nullable=True),
        sa.Column("goals", sa.Text, nullable=True),
        sa.Column("strengths", sa.Text, nullable=True),
        sa.Column("weaknesses", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_student_bio_updated", "student_bio", ["updated_at"])


def downgrade() -> None:
    op.drop_index("idx_student_bio_updated", table_name="student_bio")
    op.drop_table("student_bio")
