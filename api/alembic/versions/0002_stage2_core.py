"""stage2 core: assignments, topics, hotspots, trophies, avatars, mems, tournaments

Revision ID: 0002_stage2
Revises: 0001
Create Date: 2025-09-25 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# ревизия
revision = "0002_stage2"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- topics ----
    op.create_table(
        "topic",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
    )

    # ---- assignments ----
    op.create_table(
        "assignment",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id"), nullable=False),
        sa.Column("lesson_id", sa.Integer, sa.ForeignKey("lesson.id"), nullable=True),
        sa.Column(
            "status",
            sa.String,
            sa.CheckConstraint("status IN ('new','in_progress','done','late')"),
            nullable=False,
            server_default="new",
        ),
        sa.Column("title", sa.String, nullable=True),
        sa.Column("reward_type", sa.String, nullable=True),
        sa.Column("due_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_assignment_student_due", "assignment", ["student_id", "due_at"])
    op.create_index("idx_assignment_status", "assignment", ["status"])

    op.create_table(
        "assignment_topic",
        sa.Column("assignment_id", sa.Integer, sa.ForeignKey("assignment.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("topic_id", sa.Integer, sa.ForeignKey("topic.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "submission",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("assignment_id", sa.Integer, sa.ForeignKey("assignment.id", ondelete="CASCADE")),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("grade", sa.Numeric(4, 2), nullable=True),
        sa.Column("feedback", sa.Text, nullable=True),
    )

    # ---- error hotspots (heatmap) ----
    op.create_table(
        "error_hotspot",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id"), nullable=False),
        sa.Column("topic_id", sa.Integer, sa.ForeignKey("topic.id"), nullable=False),
        sa.Column("heat", sa.Integer, nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("student_id", "topic_id", name="uq_hotspot_student_topic"),
    )
    op.create_index("idx_hotspot_student_heat", "error_hotspot", ["student_id", "heat"])

    # ---- avatars & trophies ----
    op.create_table(
        "avatar_theme",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String, unique=True, nullable=False),
        sa.Column("icon", sa.String, nullable=False),
    )

    # добавим FK из student_profile на avatar_theme (если колонки нет — создайте)
    with op.batch_alter_table("student_profile") as batch:
        if not _column_exists("student_profile", "avatar_theme_id"):
            batch.add_column(sa.Column("avatar_theme_id", sa.Integer, sa.ForeignKey("avatar_theme.id"), nullable=True))
        if not _column_exists("student_profile", "progress_points"):
            batch.add_column(sa.Column("progress_points", sa.Integer, server_default="0", nullable=False))

    op.create_table(
        "trophy",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id"), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_trophy_student", "trophy", ["student_id"])

    # ---- mems (простая галерея) ----
    op.create_table(
        "mem",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id"), nullable=True),
        sa.Column("url", sa.String, nullable=False),
        sa.Column("caption", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # ---- tournaments (минимально) ----
    op.create_table(
        "tournament",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("level", sa.Integer, nullable=True),
        sa.Column("start_at", sa.DateTime, nullable=True),
        sa.Column("end_at", sa.DateTime, nullable=True),
    )
    op.create_table(
        "tournament_participant",
        sa.Column("tournament_id", sa.Integer, sa.ForeignKey("tournament.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("points", sa.Integer, server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_table("tournament_participant")
    op.drop_table("tournament")
    op.drop_table("mem")
    op.drop_index("idx_trophy_student", table_name="trophy")
    op.drop_table("trophy")
    # удалить добавленные в student_profile колонки безопасно
    with op.batch_alter_table("student_profile") as batch:
        if _column_exists("student_profile", "progress_points"):
            batch.drop_column("progress_points")
        if _column_exists("student_profile", "avatar_theme_id"):
            batch.drop_column("avatar_theme_id")
    op.drop_table("avatar_theme")
    op.drop_index("idx_hotspot_student_heat", table_name="error_hotspot")
    op.drop_table("error_hotspot")
    op.drop_table("submission")
    op.drop_table("assignment_topic")
    op.drop_index("idx_assignment_status", table_name="assignment")
    op.drop_index("idx_assignment_student_due", table_name="assignment")
    op.drop_table("assignment")
    op.drop_table("topic")


# --- helpers ---
from sqlalchemy import inspect
from sqlalchemy.engine import reflection

def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table)]
    return column in cols
