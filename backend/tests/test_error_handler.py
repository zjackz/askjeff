"""测试错误处理中间件"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import (
    ValidationException,
    BusinessException,
    SystemException,
    ErrorCode
)
from app.middleware.error_handler import error_handler_middleware


@pytest.fixture
def app():
    """创建测试应用"""
    app = FastAPI()
    app.middleware("http")(error_handler_middleware)
    
    @app.get("/test/validation")
    async def test_validation():
        raise ValidationException(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message="测试验证错误"
        )
    
    @app.get("/test/business")
    async def test_business():
        raise BusinessException(
            code=ErrorCode.BATCH_NOT_FOUND,
            message="测试业务错误"
        )
    
    @app.get("/test/system")
    async def test_system():
        raise SystemException(
            code=ErrorCode.DATABASE_ERROR,
            message="测试系统错误"
        )
    
    @app.get("/test/unexpected")
    async def test_unexpected():
        raise ValueError("未预期的错误")
    
    @app.get("/test/db-error")
    async def test_db_error():
        raise SQLAlchemyError("数据库连接失败")
    
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


def test_validation_exception(client):
    """测试验证异常处理"""
    response = client.get("/test/validation")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.INVALID_FILE_FORMAT
    assert data["error"]["message"] == "测试验证错误"


def test_business_exception(client):
    """测试业务异常处理"""
    response = client.get("/test/business")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.BATCH_NOT_FOUND
    assert data["error"]["message"] == "测试业务错误"


def test_system_exception(client):
    """测试系统异常处理"""
    response = client.get("/test/system")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.DATABASE_ERROR
    assert data["error"]["message"] == "测试系统错误"


def test_unexpected_exception(client):
    """测试未预期异常处理"""
    response = client.get("/test/unexpected")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.INTERNAL_SERVER_ERROR


def test_database_exception(client):
    """测试数据库异常处理"""
    response = client.get("/test/db-error")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.DATABASE_ERROR
