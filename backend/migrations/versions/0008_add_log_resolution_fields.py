"""补充系统日志状态与解决信息，用于问题跟踪。

Revision ID: 0008
Revises: 0007
Create Date: 2025-11-18
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 允许重复执行，不影响既有数据
    op.execute(sa.text("ALTER TABLE system_logs ADD COLUMN IF NOT EXISTS status VARCHAR(32) DEFAULT 'new'"))
    op.execute(sa.text("ALTER TABLE system_logs ADD COLUMN IF NOT EXISTS resolved_by VARCHAR(128)"))
    op.execute(sa.text("ALTER TABLE system_logs ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ"))
    op.execute(sa.text("ALTER TABLE system_logs ADD COLUMN IF NOT EXISTS resolution_note TEXT"))


def downgrade() -> None:
    op.execute(sa.text("ALTER TABLE system_logs DROP COLUMN IF EXISTS resolution_note"))
    op.execute(sa.text("ALTER TABLE system_logs DROP COLUMN IF EXISTS resolved_at"))
    op.execute(sa.text("ALTER TABLE system_logs DROP COLUMN IF EXISTS resolved_by"))
    op.execute(sa.text("ALTER TABLE system_logs DROP COLUMN IF EXISTS status"))
