"""新增系统日志表，支持入库与查询。

Revision ID: 0006
Revises: 0005
Create Date: 2025-11-17
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_logs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("trace_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_system_logs_timestamp", "system_logs", ["timestamp"])
    op.create_index("idx_system_logs_level", "system_logs", ["level"])
    op.create_index("idx_system_logs_category", "system_logs", ["category"])


def downgrade() -> None:
    op.drop_index("idx_system_logs_category", table_name="system_logs")
    op.drop_index("idx_system_logs_level", table_name="system_logs")
    op.drop_index("idx_system_logs_timestamp", table_name="system_logs")
    op.drop_table("system_logs")
