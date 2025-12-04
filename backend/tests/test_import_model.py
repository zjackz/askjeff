"""
测试 ImportBatch 数据库模型和迁移

验证数据库表结构包含所有必需字段
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import inspect

from app.db import SessionLocal
from app.models.import_batch import ImportBatch


class TestImportBatchModel:
    """测试 ImportBatch 数据库模型"""

    @pytest.fixture
    def db_session(self):
        """创建数据库会话"""
        session = SessionLocal()
        yield session
        session.close()

    def test_model_has_created_at_column(self, db_session):
        """测试模型包含 created_at 列"""
        inspector = inspect(db_session.bind)
        columns = {col["name"]: col for col in inspector.get_columns("import_batches")}
        
        assert "created_at" in columns
        assert columns["created_at"]["nullable"] is False

    def test_model_has_ai_status_column(self, db_session):
        """测试模型包含 ai_status 列"""
        inspector = inspect(db_session.bind)
        columns = {col["name"]: col for col in inspector.get_columns("import_batches")}
        
        assert "ai_status" in columns
        assert columns["ai_status"]["nullable"] is False

    def test_model_has_ai_summary_column(self, db_session):
        """测试模型包含 ai_summary 列"""
        inspector = inspect(db_session.bind)
        columns = {col["name"]: col for col in inspector.get_columns("import_batches")}
        
        assert "ai_summary" in columns
        assert columns["ai_summary"]["nullable"] is True

    def test_create_batch_with_all_fields(self, db_session):
        """测试创建包含所有字段的批次记录"""
        batch = ImportBatch(
            filename="test.xlsx",
            storage_path="/storage/test.xlsx",
            import_strategy="append",
            status="pending",
            total_rows=100,
            success_rows=0,
            failed_rows=0,
            ai_status="none",
            ai_summary=None,
        )
        
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        # 验证所有字段
        assert batch.id is not None
        assert batch.filename == "test.xlsx"
        assert batch.created_at is not None
        assert batch.ai_status == "none"
        assert batch.ai_summary is None

    def test_created_at_auto_populated(self, db_session):
        """测试 created_at 自动填充"""
        before = datetime.now(timezone.utc)
        
        batch = ImportBatch(
            filename="test.xlsx",
            storage_path="/storage/test.xlsx",
            import_strategy="append",
            status="pending",
            total_rows=0,
            success_rows=0,
            failed_rows=0,
        )
        
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        after = datetime.now(timezone.utc)
        
        # 验证 created_at 在合理时间范围内
        assert batch.created_at is not None
        assert before <= batch.created_at.replace(tzinfo=timezone.utc) <= after

    def test_ai_status_default_value(self, db_session):
        """测试 ai_status 默认值"""
        batch = ImportBatch(
            filename="test.xlsx",
            storage_path="/storage/test.xlsx",
            import_strategy="append",
            status="pending",
            total_rows=0,
            success_rows=0,
            failed_rows=0,
        )
        
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        # 验证默认值
        assert batch.ai_status == "none"

    def test_update_ai_fields(self, db_session):
        """测试更新 AI 相关字段"""
        batch = ImportBatch(
            filename="test.xlsx",
            storage_path="/storage/test.xlsx",
            import_strategy="append",
            status="succeeded",
            total_rows=100,
            success_rows=100,
            failed_rows=0,
        )
        
        db_session.add(batch)
        db_session.commit()
        
        # 更新 AI 字段
        batch.ai_status = "completed"
        batch.ai_summary = {"total": 100, "extracted": 95}
        
        db_session.commit()
        db_session.refresh(batch)
        
        assert batch.ai_status == "completed"
        assert batch.ai_summary == {"total": 100, "extracted": 95}
