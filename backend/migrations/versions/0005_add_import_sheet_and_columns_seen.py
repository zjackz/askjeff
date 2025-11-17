"""为导入批次增加 sheet 名称与列扫描结果。

Revision ID: 0005
Revises: 0004
Create Date: 2025-11-17
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("import_batches", sa.Column("sheet_name", sa.Text(), nullable=True))
    op.add_column("import_batches", sa.Column("columns_seen", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("import_batches", "columns_seen")
    op.drop_column("import_batches", "sheet_name")
