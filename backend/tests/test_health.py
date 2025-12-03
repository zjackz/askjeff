"""测试健康检查端点"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


def test_health_check(client):
    """测试基础健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert "storage" in data["checks"]
    
    # 在测试环境中,数据库和存储应该都是健康的
    assert data["checks"]["database"] == "healthy"
    assert data["checks"]["storage"] == "healthy"


def test_readiness_check(client):
    """测试就绪检查"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "ready"


def test_liveness_check(client):
    """测试存活检查"""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "alive"
