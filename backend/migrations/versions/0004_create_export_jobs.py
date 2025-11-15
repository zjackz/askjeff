"""create export_jobs table

Revision ID: 0004
Revises: 0003
Create Date: 2025-11-15
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "export_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("export_type", sa.String(length=32), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=True),
        sa.Column("selected_fields", sa.JSON(), nullable=False),
        sa.Column("file_format", sa.String(length=8), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("triggered_by", sa.String(length=36), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("export_jobs")
