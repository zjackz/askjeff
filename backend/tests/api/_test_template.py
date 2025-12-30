"""
新测试模板

使用方法:
1. 复制此文件到 backend/tests/api/
2. 重命名为 test_your_feature.py
3. 替换 template 为你的功能名
4. 实现具体测试用例
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app

client = TestClient(app)


def test_create_template_success(db: Session):
    """测试创建模板成功"""
    response = client.post(
        "/api/v1/template",
        json={
            "param1": "test",
            "param2": "value"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["param1"] == "test"


def test_create_template_validation_error(db: Session):
    """测试参数验证失败"""
    response = client.post(
        "/api/v1/template",
        json={}
    )
    assert response.status_code == 422


def test_create_template_invalid_param(db: Session):
    """测试无效参数"""
    response = client.post(
        "/api/v1/template",
        json={
            "param1": "",  # 空字符串
            "param2": "value"
        }
    )
    assert response.status_code == 400


def test_get_template_success(db: Session):
    """测试获取模板成功"""
    # 先创建
    create_response = client.post(
        "/api/v1/template",
        json={"param1": "test"}
    )
    template_id = create_response.json()["id"]
    
    # 再获取
    response = client.get(f"/api/v1/template/{template_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == template_id


def test_get_template_not_found(db: Session):
    """测试获取不存在的模板"""
    response = client.get("/api/v1/template/nonexistent")
    assert response.status_code == 404


def test_list_templates(db: Session):
    """测试获取模板列表"""
    response = client.get("/api/v1/template")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_list_templates_pagination(db: Session):
    """测试分页"""
    response = client.get("/api/v1/template?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_update_template_success(db: Session):
    """测试更新模板成功"""
    # 先创建
    create_response = client.post(
        "/api/v1/template",
        json={"param1": "test"}
    )
    template_id = create_response.json()["id"]
    
    # 再更新
    response = client.put(
        f"/api/v1/template/{template_id}",
        json={"param1": "updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["param1"] == "updated"


def test_delete_template_success(db: Session):
    """测试删除模板成功"""
    # 先创建
    create_response = client.post(
        "/api/v1/template",
        json={"param1": "test"}
    )
    template_id = create_response.json()["id"]
    
    # 再删除
    response = client.delete(f"/api/v1/template/{template_id}")
    assert response.status_code == 200
    
    # 验证已删除
    get_response = client.get(f"/api/v1/template/{template_id}")
    assert get_response.status_code == 404


def test_unauthorized_access():
    """测试未授权访问"""
    # 不提供 token
    response = client.post(
        "/api/v1/template",
        json={"param1": "test"}
    )
    # 根据实际权限要求调整
    assert response.status_code in [401, 403]
