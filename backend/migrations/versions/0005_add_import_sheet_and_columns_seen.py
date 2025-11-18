"""为导入批次增加 sheet 名称与列扫描结果。

Revision ID: 0005
Revises: 0004
Create Date: 2025-11-17
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("ALTER TABLE import_batches ADD COLUMN IF NOT EXISTS sheet_name TEXT"))
    op.execute(sa.text("ALTER TABLE import_batches ADD COLUMN IF NOT EXISTS columns_seen JSON"))


def downgrade() -> None:
    op.execute(sa.text("ALTER TABLE import_batches DROP COLUMN IF EXISTS columns_seen"))
    op.execute(sa.text("ALTER TABLE import_batches DROP COLUMN IF EXISTS sheet_name"))
