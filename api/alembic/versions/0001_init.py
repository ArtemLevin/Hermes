"""create initial tables

Revision ID: 0001
Revises:
Create Date: 2025-09-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)

    # Create student_profile table
    op.create_table(
        'student_profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('progress_points', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tutor_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_profile_id'), 'student_profile', ['id'], unique=False)
    op.create_index(op.f('ix_student_profile_name'), 'student_profile', ['name'], unique=False)
    op.create_index(op.f('ix_student_profile_tutor_id'), 'student_profile', ['tutor_id'], unique=False)

    # Create assignment table
    op.create_table(
        'assignment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('reward_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profile.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assignment_id'), 'assignment', ['id'], unique=False)
    op.create_index(op.f('ix_assignment_student_id'), 'assignment', ['student_id'], unique=False)

    # Create submission table
    op.create_table(
        'submission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('artifacts', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignment.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submission_assignment_id'), 'submission', ['assignment_id'], unique=False)
    op.create_index(op.f('ix_submission_id'), 'submission', ['id'], unique=False)

    # Create trophy table
    op.create_table(
        'trophy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trophy_id'), 'trophy', ['id'], unique=False)

    # Create mem table
    op.create_table(
        'mem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True), # Corrected from 'image' to 'image_url'
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mem_id'), 'mem', ['id'], unique=False)

    # Create tournament table
    op.create_table(
        'tournament',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tournament_id'), 'tournament', ['id'], unique=False)

    # Create tournament_participants table
    op.create_table(
        'tournament_participants',
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profile.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournament.id'], ),
        sa.PrimaryKeyConstraint('tournament_id', 'student_id')
    )

    # Create topic table
    op.create_table(
        'topic',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_topic_id'), 'topic', ['id'], unique=False)

    # Create error_hotspot table
    op.create_table(
        'error_hotspot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('heat', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profile.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topic.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_error_hotspot_id'), 'error_hotspot', ['id'], unique=False)
    op.create_index(op.f('ix_error_hotspot_student_id'), 'error_hotspot', ['student_id'], unique=False)
    op.create_index(op.f('ix_error_hotspot_topic_id'), 'error_hotspot', ['topic_id'], unique=False)

    # Create avatar_theme table
    op.create_table(
        'avatar_theme',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_avatar_theme_code'), 'avatar_theme', ['code'], unique=True)
    op.create_index(op.f('ix_avatar_theme_id'), 'avatar_theme', ['id'], unique=False)

    # Create student_trophies association table
    op.create_table(
        'student_trophies',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('trophy_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profile.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trophy_id'], ['trophy.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id', 'trophy_id')
    )

    # Create student_memes association table
    op.create_table(
        'student_memes',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('mem_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['mem_id'], ['mem.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['student_profile.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id', 'mem_id')
    )


def downgrade() -> None:
    # Drop tables in reverse order to handle foreign keys
    op.drop_table('student_memes')
    op.drop_table('student_trophies')
    op.drop_table('avatar_theme')
    op.drop_table('error_hotspot')
    op.drop_table('topic')
    op.drop_table('tournament_participants')
    op.drop_table('tournament')
    op.drop_table('mem')
    op.drop_table('trophy')
    op.drop_table('submission')
    op.drop_table('assignment')
    op.drop_table('student_profile')
    op.drop_table('user')