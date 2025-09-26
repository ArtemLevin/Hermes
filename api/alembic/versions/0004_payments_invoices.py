"""stage2: payments & invoices

Revision ID: 0004_payments_invoices
Revises: 0003_student_bio
Create Date: 2025-09-26 11:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# ревизия
revision = "0004_payments_invoices"
down_revision = "0003_student_bio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- invoices ----
    op.create_table(
        "invoice",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status",
            sa.String,
            sa.CheckConstraint("status IN ('draft','issued','paid','overdue','canceled')"),
            nullable=False,
            server_default="issued",
        ),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_index("idx_invoice_student_due", "invoice", ["student_id", "due_date"])
    op.create_index("idx_invoice_status", "invoice", ["status"])

    # ---- payments ----
    op.create_table(
        "payment",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("student_profile.id"), nullable=False),
        sa.Column("invoice_id", sa.Integer, sa.ForeignKey("invoice.id"), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status",
            sa.String,
            sa.CheckConstraint("status IN ('pending','paid','failed','refunded')"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("method", sa.String, nullable=True),  # cash | transfer | card (мануально)
        sa.Column("paid_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_payment_student_created", "payment", ["student_id", "created_at"])
    op.create_index("idx_payment_status", "payment", ["status"])


def downgrade() -> None:
    op.drop_index("idx_payment_status", table_name="payment")
    op.drop_index("idx_payment_student_created", table_name="payment")
    op.drop_table("payment")

    op.drop_index("idx_invoice_status", table_name="invoice")
    op.drop_index("idx_invoice_student_due", table_name="invoice")
    op.drop_table("invoice")
