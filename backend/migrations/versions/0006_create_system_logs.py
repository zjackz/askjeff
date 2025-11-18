"""新增系统日志表，支持入库与查询。

Revision ID: 0006
Revises: 0005
Create Date: 2025-11-17
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "system_logs" not in inspector.get_table_names():
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
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("system_logs")}
    if "idx_system_logs_timestamp" not in existing_indexes:
        op.create_index("idx_system_logs_timestamp", "system_logs", ["timestamp"])
    if "idx_system_logs_level" not in existing_indexes:
        op.create_index("idx_system_logs_level", "system_logs", ["level"])
    if "idx_system_logs_category" not in existing_indexes:
        op.create_index("idx_system_logs_category", "system_logs", ["category"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("system_logs")}
    existing_tables = inspector.get_table_names()
    if "idx_system_logs_category" in existing_indexes:
        op.drop_index("idx_system_logs_category", table_name="system_logs")
    if "idx_system_logs_level" in existing_indexes:
        op.drop_index("idx_system_logs_level", table_name="system_logs")
    if "idx_system_logs_timestamp" in existing_indexes:
        op.drop_index("idx_system_logs_timestamp", table_name="system_logs")
    if "system_logs" in existing_tables:
        op.drop_table("system_logs")
