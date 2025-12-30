"""
测试 /api/imports API 端点

验证 API 返回正确的字段和格式
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models.import_batch import ImportBatch


class TestImportsAPI:
    """测试导入 API 端点"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        """创建数据库会话"""
        session = SessionLocal()
        yield session
        # 清理测试数据
        session.query(ImportBatch).delete()
        session.commit()
        session.close()

    def test_list_imports_returns_snake_case_fields(self, client, db_session):
        """测试 API 返回 snake_case 字段"""
        # 创建测试数据
        batch = ImportBatch(
            filename="test.xlsx",
            storage_path="/storage/test.xlsx",
            import_strategy="append",
            status="succeeded",
            total_rows=100,
            success_rows=95,
            failed_rows=5,
            ai_status="none",
        )
        db_session.add(batch)
        db_session.commit()
        
        # 调用 API
        response = client.get("/api/v1/imports")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert len(data["items"]) > 0
        
        item = data["items"][0]
        
        # 验证使用 camelCase (API契约)
        assert "totalRows" in item
        assert "successRows" in item
        assert "failedRows" in item
        assert "createdAt" in item
        assert "aiStatus" in item
        
        # 验证不使用 snake_case
        assert "total_rows" not in item
        assert "success_rows" not in item

    def test_list_imports_includes_created_at(self, client, db_session):
        """测试 API 响应包含 created_at 字段"""
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
        
        response = client.get("/api/v1/imports")
        
        assert response.status_code == 200
        data = response.json()
        item = data["items"][0]
        
        assert "createdAt" in item
        assert item["createdAt"] is not None

    def test_list_imports_includes_ai_fields(self, client, db_session):
        """测试 API 响应包含 AI 相关字段"""
        batch = ImportBatch(
            filename="test.xlsx",
            storage_path="/storage/test.xlsx",
            import_strategy="append",
            status="succeeded",
            total_rows=100,
            success_rows=100,
            failed_rows=0,
            ai_status="completed",
            ai_summary={"total": 100, "extracted": 95},
        )
        db_session.add(batch)
        db_session.commit()
        
        response = client.get("/api/v1/imports")
        
        assert response.status_code == 200
        data = response.json()
        item = data["items"][0]
        
        assert "aiStatus" in item
        assert item["aiStatus"] == "completed"
        assert "aiSummary" in item
        assert item["aiSummary"] == {"total": 100, "extracted": 95}

    def test_list_imports_pagination(self, client, db_session):
        """测试 API 分页功能"""
        # 创建多条测试数据
        for i in range(25):
            batch = ImportBatch(
                filename=f"test_{i}.xlsx",
                storage_path=f"/storage/test_{i}.xlsx",
                import_strategy="append",
                status="succeeded",
                total_rows=100,
                success_rows=100,
                failed_rows=0,
            )
            db_session.add(batch)
        db_session.commit()
        
        # 测试第一页
        response = client.get("/api/v1/imports?page=1&pageSize=10")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 10
        assert data["total"] == 25

    def test_empty_imports_list(self, client, db_session):
        """测试空列表响应"""
        response = client.get("/api/v1/imports")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert data["items"] == []
        assert data["total"] == 0
