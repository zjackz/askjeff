"""
数据库迁移脚本：添加 API 导入支持

添加字段:
- source_type: 导入来源类型 (file, api)
- metadata: API 导入元数据
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import engine


def upgrade():
    """添加 API 导入支持字段"""
    with engine.connect() as conn:
        # 添加 source_type 字段
        conn.execute(text("""
            ALTER TABLE import_batches 
            ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) DEFAULT 'file'
        """))
        
        # 添加 metadata 字段
        conn.execute(text("""
            ALTER TABLE import_batches 
            ADD COLUMN IF NOT EXISTS metadata JSONB
        """))
        
        conn.commit()
        print("✅ 数据库迁移完成：添加 API 导入支持字段")


def downgrade():
    """回滚迁移"""
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE import_batches DROP COLUMN IF EXISTS metadata"))
        conn.execute(text("ALTER TABLE import_batches DROP COLUMN IF EXISTS source_type"))
        conn.commit()
        print("✅ 数据库迁移回滚完成")


if __name__ == "__main__":
    print("开始数据库迁移...")
    upgrade()

