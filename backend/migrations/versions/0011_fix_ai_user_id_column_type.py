"""修复 AI 相关表的 user_id 字段类型。

背景：
- `users.id` 为 `INTEGER`
- 历史版本中 `product_selection_reports.user_id`、`keyword_optimizations.user_id` 误建为 `UUID`

该不一致会导致 PostgreSQL 外键创建失败，并影响测试环境的 `Base.metadata.create_all()`。

处理策略：
- 将两个表的 `user_id` 统一改为 `INTEGER`
- 由于从 UUID 到 INTEGER 无法可靠转换，本迁移使用 `USING NULL` 将历史值置空
- 添加表存在性检查，避免在表不存在时报错
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def _drop_fk_if_exists(table: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for fk in inspector.get_foreign_keys(table):
        if fk.get("referred_table") == "users":
            name = fk.get("name")
            if name:
                op.drop_constraint(name, table_name=table, type_="foreignkey")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    for table in ("product_selection_reports", "keyword_optimizations"):
        # 跳过不存在的表
        if table not in existing_tables:
            continue
            
        _drop_fk_if_exists(table)

        # 统一列类型：UUID -> INTEGER（历史值置空）
        op.execute(sa.text(f"ALTER TABLE {table} ALTER COLUMN user_id TYPE INTEGER USING NULL"))

        # 重新建立外键
        op.create_foreign_key(
            constraint_name=f"fk_{table}_user_id_users",
            source_table=table,
            referent_table="users",
            local_cols=["user_id"],
            remote_cols=["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    for table in ("product_selection_reports", "keyword_optimizations"):
        # 跳过不存在的表
        if table not in existing_tables:
            continue
            
        op.drop_constraint(f"fk_{table}_user_id_users", table_name=table, type_="foreignkey")
        op.execute(sa.text(f"ALTER TABLE {table} ALTER COLUMN user_id TYPE UUID USING NULL"))
        op.create_foreign_key(
            constraint_name=f"fk_{table}_user_id_users",
            source_table=table,
            referent_table="users",
            local_cols=["user_id"],
            remote_cols=["id"],
            ondelete="SET NULL",
        )
