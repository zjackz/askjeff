"""
Amazon Ads Analysis API 集成测试
测试所有 API 端点的完整流程
"""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.amazon_ads import (
    AmazonStore,
    ProductCost,
    InventorySnapshot,
    AdsMetricSnapshot,
    BusinessMetricSnapshot
)
from app.models.user import User


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient, test_user_with_password: User):
    """获取认证 headers"""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user_with_password.username, "password": "test_password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user_with_password(db: Session):
    """创建带密码的测试用户"""
    from app.core.security import get_password_hash
    
    user = User(
        username="test_ads_api_user",
        hashed_password=get_password_hash("test_password"),
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_store_with_data(db: Session, test_user_with_password: User):
    """创建带完整数据的测试店铺"""
    # 1. 创建店铺
    store = AmazonStore(
        id=uuid4(),
        user_id=test_user_with_password.id,
        store_name="API Test Store",
        marketplace_id="ATVPDKIKX0DER",
        marketplace_name="United States",
        seller_id="API_TEST_SELLER",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(store)
    db.commit()
    
    # 2. 创建测试数据
    today = date.today()
    skus = ["API-SKU-001", "API-SKU-002", "API-SKU-003"]
    
    for sku_idx, sku in enumerate(skus):
        asin = f"B00API{sku_idx:03d}"
        
        # 成本
        cost = ProductCost(
            id=uuid4(),
            store_id=store.id,
            sku=sku,
            asin=asin,
            cogs=10.0 + sku_idx,
            currency="USD",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(cost)
        
        # 快照数据
        for i in range(30):
            snapshot_date = today - timedelta(days=i)
            
            # 库存
            inv = InventorySnapshot(
                id=uuid4(),
                store_id=store.id,
                date=snapshot_date,
                sku=sku,
                asin=asin,
                fba_inventory=500 + (sku_idx * 500),
                inbound_inventory=100,
                reserved_inventory=50,
                unfulfillable_inventory=5,
                created_at=datetime.utcnow()
            )
            db.add(inv)
            
            # 广告
            ads = AdsMetricSnapshot(
                id=uuid4(),
                store_id=store.id,
                date=snapshot_date,
                sku=sku,
                asin=asin,
                spend=30.0 + (sku_idx * 10),
                sales=150.0 + (sku_idx * 50),
                impressions=5000,
                clicks=50,
                orders=5,
                units=8,
                created_at=datetime.utcnow()
            )
            db.add(ads)
            
            # 业务
            biz = BusinessMetricSnapshot(
                id=uuid4(),
                store_id=store.id,
                date=snapshot_date,
                sku=sku,
                asin=asin,
                total_sales_amount=200.0 + (sku_idx * 100),
                total_units_ordered=10 + sku_idx,
                sessions=300,
                page_views=500,
                created_at=datetime.utcnow()
            )
            db.add(biz)
    
    db.commit()
    db.refresh(store)
    return store


class TestStoresAPI:
    """店铺列表 API 测试"""
    
    def test_get_stores_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_store_with_data: AmazonStore
    ):
        """测试获取店铺列表 - 成功"""
        response = client.get(
            "/api/v1/ads-analysis/stores",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        stores = response.json()
        assert isinstance(stores, list)
        assert len(stores) >= 1
        
        # 验证店铺数据结构
        store = stores[0]
        assert "id" in store
        assert "store_name" in store
        assert "marketplace_name" in store
        assert "is_active" in store
    
    def test_get_stores_unauthorized(self, client: TestClient):
        """测试获取店铺列表 - 未认证"""
        response = client.get("/api/v1/ads-analysis/stores")
        assert response.status_code == 401
    
    def test_get_stores_empty(
        self, 
        client: TestClient,
        db: Session
    ):
        """测试获取店铺列表 - 空列表"""
        from app.core.security import get_password_hash
        
        # 创建没有店铺的用户
        user = User(
            username="no_stores_user",
            hashed_password=get_password_hash("password"),
            role="admin"
        )
        db.add(user)
        db.commit()
        
        # 登录
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "no_stores_user", "password": "password"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取店铺列表
        response = client.get(
            "/api/v1/ads-analysis/stores",
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json() == []


class TestMatrixAPI:
    """矩阵数据 API 测试"""
    
    def test_get_matrix_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_store_with_data: AmazonStore
    ):
        """测试获取矩阵数据 - 成功"""
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={test_store_with_data.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        matrix_data = response.json()
        assert isinstance(matrix_data, list)
        assert len(matrix_data) >= 1
        
        # 验证数据结构
        point = matrix_data[0]
        assert "sku" in point
        assert "asin" in point
        assert "stock_weeks" in point
        assert "tacos" in point
        assert "sales" in point
        assert "status" in point
        assert "inventory_qty" in point
        assert "ad_spend" in point
        assert "total_sales" in point
        assert "ctr" in point
        assert "cvr" in point
        assert "acos" in point
        assert "roas" in point
        assert "margin" in point
        
        # 验证数据类型
        assert isinstance(point["stock_weeks"], (int, float))
        assert isinstance(point["tacos"], (int, float))
        assert isinstance(point["sales"], (int, float))
        assert point["status"] in [
            "CRITICAL / CLEARANCE",
            "STAR / GROWTH",
            "POTENTIAL / DEFENSE",
            "DROP / KILL"
        ]
    
    def test_get_matrix_missing_store_id(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """测试获取矩阵数据 - 缺少 store_id"""
        response = client.get(
            "/api/v1/ads-analysis/matrix",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error
    
    def test_get_matrix_invalid_store_id(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """测试获取矩阵数据 - 无效的 store_id"""
        fake_store_id = uuid4()
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={fake_store_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_get_matrix_unauthorized(
        self, 
        client: TestClient,
        test_store_with_data: AmazonStore
    ):
        """测试获取矩阵数据 - 未认证"""
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={test_store_with_data.id}"
        )
        assert response.status_code == 401
    
    def test_get_matrix_with_custom_days(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_store_with_data: AmazonStore
    ):
        """测试获取矩阵数据 - 自定义天数"""
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={test_store_with_data.id}&days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        matrix_data = response.json()
        assert isinstance(matrix_data, list)
    
    def test_get_matrix_days_validation(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_store_with_data: AmazonStore
    ):
        """测试获取矩阵数据 - 天数验证"""
        # 天数太小
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={test_store_with_data.id}&days=5",
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # 天数太大
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={test_store_with_data.id}&days=100",
            headers=auth_headers
        )
        assert response.status_code == 422


class TestDiagnosisAPI:
    """诊断 API 测试"""
    
    def test_get_diagnosis_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_store_with_data: AmazonStore
    ):
        """测试获取 SKU 诊断 - 成功"""
        sku = "API-SKU-001"
        response = client.get(
            f"/api/v1/ads-analysis/{sku}/diagnosis?store_id={test_store_with_data.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        diagnosis = response.json()
        
        # 验证数据结构
        assert diagnosis["sku"] == sku
        assert "asin" in diagnosis
        assert "status" in diagnosis
        assert "diagnosis" in diagnosis
        assert "metrics" in diagnosis
        
        # 验证诊断内容
        assert len(diagnosis["diagnosis"]) > 0
        
        # 验证指标
        metrics = diagnosis["metrics"]
        assert "stock_weeks" in metrics
        assert "tacos" in metrics
        assert "sales" in metrics
        assert "ad_spend" in metrics
        assert "ctr" in metrics
        assert "cvr" in metrics
        assert "acos" in metrics
        assert "roas" in metrics
        assert "margin" in metrics
    
    def test_get_diagnosis_sku_not_found(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_store_with_data: AmazonStore
    ):
        """测试获取 SKU 诊断 - SKU 不存在"""
        response = client.get(
            f"/api/v1/ads-analysis/NONEXISTENT-SKU/diagnosis?store_id={test_store_with_data.id}",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_diagnosis_missing_store_id(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """测试获取 SKU 诊断 - 缺少 store_id"""
        response = client.get(
            "/api/v1/ads-analysis/API-SKU-001/diagnosis",
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_get_diagnosis_unauthorized(
        self, 
        client: TestClient,
        test_store_with_data: AmazonStore
    ):
        """测试获取 SKU 诊断 - 未认证"""
        response = client.get(
            f"/api/v1/ads-analysis/API-SKU-001/diagnosis?store_id={test_store_with_data.id}"
        )
        assert response.status_code == 401


class TestCrossStoreIsolation:
    """跨店铺隔离测试"""
    
    def test_cannot_access_other_user_store(
        self, 
        client: TestClient,
        db: Session,
        test_store_with_data: AmazonStore
    ):
        """测试无法访问其他用户的店铺"""
        from app.core.security import get_password_hash
        
        # 创建另一个用户
        other_user = User(
            username="other_user",
            hashed_password=get_password_hash("password"),
            role="admin"
        )
        db.add(other_user)
        db.commit()
        
        # 登录为另一个用户
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "other_user", "password": "password"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 尝试访问第一个用户的店铺
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={test_store_with_data.id}",
            headers=headers
        )
        
        assert response.status_code == 404
        assert "not found or access denied" in response.json()["detail"]


class TestPerformance:
    """性能测试"""
    
    def test_matrix_response_time(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_store_with_data: AmazonStore
    ):
        """测试矩阵 API 响应时间"""
        import time
        
        start_time = time.time()
        response = client.get(
            f"/api/v1/ads-analysis/matrix?store_id={test_store_with_data.id}",
            headers=auth_headers
        )
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # 响应时间应该小于 2 秒
        assert response_time < 2.0, f"Response time {response_time}s exceeds 2s threshold"
