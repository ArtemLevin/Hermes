"""stage2 add student_bio

Revision ID: 0003_student_bio
Revises: 0002_stage2
Create Date: 2025-09-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_student_bio'
down_revision: Union[str, None] = '0002_stage2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create student_bio table
    op.create_table(
        'student_bio',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.Date(), nullable=True),
        sa.Column('goals', sa.Text(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('weaknesses', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profile.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id')
    )


def downgrade() -> None:
    op.drop_table('student_bio')