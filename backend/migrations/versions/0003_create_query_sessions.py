"""create query_sessions table

Revision ID: 0003
Revises: 0002
Create Date: 2025-11-15
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "query_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("intent", sa.Text(), nullable=True),
        sa.Column("sql_template", sa.Text(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("references", sa.JSON(), nullable=True),
        sa.Column("deepseek_trace", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="succeeded"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("asked_by", sa.String(length=36), nullable=True),
        sa.Column("asked_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("query_sessions")
