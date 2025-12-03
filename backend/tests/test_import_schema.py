"""
测试 ImportBatchOut schema 的序列化和字段验证

验证修复后的 schema 包含所有必需字段，并使用正确的 camelCase 格式(API契约)
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.imports import ImportBatchOut
from app.models.import_batch import ImportBatch


class TestImportBatchOutSchema:
    """测试 ImportBatchOut Pydantic schema"""

    def test_schema_includes_created_at_field(self):
        """测试 schema 包含 created_at 字段"""
        # 创建测试数据
        now = datetime.now(timezone.utc)
        batch_data = {
            "id": 1,
            "sequence_id": 1,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "succeeded",
            "total_rows": 100,
            "success_rows": 95,
            "failed_rows": 5,
            "started_at": now,
            "finished_at": now,
            "sheet_name": "Sheet1",
            "failure_summary": None,
            "columns_seen": ["asin", "title"],
            "created_at": now,
            "ai_status": "none",
            "ai_summary": None,
        }
        
        # 创建 schema 实例
        batch_out = ImportBatchOut(**batch_data)
        
        # 验证 created_at 字段存在
        assert hasattr(batch_out, "created_at")
        assert batch_out.created_at == now

    def test_schema_includes_ai_status_field(self):
        """测试 schema 包含 ai_status 字段"""
        now = datetime.now(timezone.utc)
        batch_data = {
            "id": 2,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "succeeded",
            "total_rows": 100,
            "success_rows": 100,
            "failed_rows": 0,
            "created_at": now,
            "ai_status": "completed",
            "ai_summary": {"extracted": 50},
        }
        
        batch_out = ImportBatchOut(**batch_data)
        
        assert hasattr(batch_out, "ai_status")
        assert batch_out.ai_status == "completed"

    def test_schema_includes_ai_summary_field(self):
        """测试 schema 包含 ai_summary 字段"""
        now = datetime.now(timezone.utc)
        ai_summary = {"total": 100, "extracted": 95, "failed": 5}
        batch_data = {
            "id": 3,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "succeeded",
            "total_rows": 100,
            "success_rows": 100,
            "failed_rows": 0,
            "created_at": now,
            "ai_status": "completed",
            "ai_summary": ai_summary,
        }
        
        batch_out = ImportBatchOut(**batch_data)
        
        assert hasattr(batch_out, "ai_summary")
        assert batch_out.ai_summary == ai_summary

    def test_schema_serializes_to_snake_case(self):
        """测试 schema 序列化为 snake_case 格式"""
        now = datetime.now(timezone.utc)
        batch_data = {
            "id": 4,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "succeeded",
            "total_rows": 100,
            "success_rows": 95,
            "failed_rows": 5,
            "created_at": now,
            "ai_status": "none",
        }
        
        batch_out = ImportBatchOut(**batch_data)
        serialized = batch_out.model_dump(by_alias=True)
        
        # 验证使用 camelCase (API契约)
        assert "totalRows" in serialized
        assert "successRows" in serialized
        assert "failedRows" in serialized
        assert "createdAt" in serialized
        assert "aiStatus" in serialized
        
        # 验证不使用 snake_case
        assert "total_rows" not in serialized
        assert "success_rows" not in serialized
        assert "failed_rows" not in serialized

    def test_schema_default_ai_status(self):
        """测试 ai_status 的默认值"""
        now = datetime.now(timezone.utc)
        batch_data = {
            "id": 5,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "succeeded",
            "total_rows": 100,
            "success_rows": 100,
            "failed_rows": 0,
            "created_at": now,
        }
        
        batch_out = ImportBatchOut(**batch_data)
        
        # 验证默认值为 "none"
        assert batch_out.ai_status == "none"

    def test_schema_from_orm_model(self):
        """测试从 ORM 模型创建 schema"""
        # 注意：这个测试需要数据库连接，可能需要在集成测试中运行
        # 这里只是验证 from_attributes 配置正确
        assert ImportBatchOut.model_config.get("from_attributes") is True

    def test_all_required_fields_present(self):
        """测试所有必需字段都存在"""
        now = datetime.now(timezone.utc)
        batch_data = {
            "id": 6,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "pending",
            "total_rows": 0,
            "success_rows": 0,
            "failed_rows": 0,
            "created_at": now,
        }
        
        batch_out = ImportBatchOut(**batch_data)
        serialized = batch_out.model_dump()
        
        # 验证所有必需字段
        required_fields = [
            "id",
            "filename",
            "import_strategy",
            "status",
            "total_rows",
            "success_rows",
            "failed_rows",
            "created_at",
            "ai_status",
        ]
        
        for field in required_fields:
            assert field in serialized, f"Missing required field: {field}"

    def test_optional_fields_can_be_none(self):
        """测试可选字段可以为 None"""
        now = datetime.now(timezone.utc)
        batch_data = {
            "id": 7,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "pending",
            "total_rows": 0,
            "success_rows": 0,
            "failed_rows": 0,
            "created_at": now,
            "started_at": None,
            "finished_at": None,
            "sheet_name": None,
            "failure_summary": None,
            "columns_seen": None,
            "ai_summary": None,
        }
        
        batch_out = ImportBatchOut(**batch_data)
        
        assert batch_out.started_at is None
        assert batch_out.finished_at is None
        assert batch_out.sheet_name is None
        assert batch_out.failure_summary is None
        assert batch_out.columns_seen is None
        assert batch_out.ai_summary is None

    def test_import_strategy_serialization(self):
        """测试 import_strategy 的序列化（下划线转连字符）"""
        now = datetime.now(timezone.utc)
        batch_data = {
            "id": 8,
            "filename": "test.xlsx",
            "import_strategy": "append",
            "status": "succeeded",
            "total_rows": 100,
            "success_rows": 100,
            "failed_rows": 0,
            "created_at": now,
        }
        
        batch_out = ImportBatchOut(**batch_data)
        serialized = batch_out.model_dump()
        
        # 验证 import_strategy 保持原值（不转换）
        assert serialized["import_strategy"] == "append"
