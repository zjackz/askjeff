"""
Amazon Ads Analysis Service 单元测试
测试 AdsAnalysisService 的所有核心功能
"""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.amazon_ads import (
    AmazonStore,
    ProductCost,
    InventorySnapshot,
    AdsMetricSnapshot,
    BusinessMetricSnapshot
)
from app.models.user import User
from app.services.ads_analysis_service import AdsAnalysisService


@pytest.fixture
def test_user(db: Session):
    """创建测试用户"""
    user = User(
        username="test_ads_user",
        hashed_password="hashed_password",
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_store(db: Session, test_user: User):
    """创建测试店铺"""
    store = AmazonStore(
        id=uuid4(),
        user_id=test_user.id,
        store_name="Test US Store",
        marketplace_id="ATVPDKIKX0DER",
        marketplace_name="United States",
        seller_id="TEST_SELLER_123",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@pytest.fixture
def test_sku_data(db: Session, test_store: AmazonStore):
    """创建测试 SKU 数据"""
    today = date.today()
    sku = "TEST-SKU-001"
    asin = "B00TEST001"
    
    # 1. 成本数据
    cost = ProductCost(
        id=uuid4(),
        store_id=test_store.id,
        sku=sku,
        asin=asin,
        cogs=10.0,
        currency="USD",
        fba_fee=3.0,
        referral_fee_rate=0.15,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(cost)
    
    # 2. 库存快照 (最近 30 天)
    for i in range(30):
        snapshot_date = today - timedelta(days=i)
        inv = InventorySnapshot(
            id=uuid4(),
            store_id=test_store.id,
            date=snapshot_date,
            sku=sku,
            asin=asin,
            fba_inventory=1000 - (i * 10),  # 递减库存
            inbound_inventory=100,
            reserved_inventory=50,
            unfulfillable_inventory=5,
            created_at=datetime.utcnow()
        )
        db.add(inv)
    
    # 3. 广告快照
    for i in range(30):
        snapshot_date = today - timedelta(days=i)
        ads = AdsMetricSnapshot(
            id=uuid4(),
            store_id=test_store.id,
            date=snapshot_date,
            sku=sku,
            asin=asin,
            spend=50.0,
            sales=200.0,
            impressions=10000,
            clicks=100,
            orders=10,
            units=15,
            created_at=datetime.utcnow()
        )
        db.add(ads)
    
    # 4. 业务快照
    for i in range(30):
        snapshot_date = today - timedelta(days=i)
        biz = BusinessMetricSnapshot(
            id=uuid4(),
            store_id=test_store.id,
            date=snapshot_date,
            sku=sku,
            asin=asin,
            total_sales_amount=300.0,
            total_units_ordered=20,
            sessions=500,
            page_views=800,
            unit_session_percentage=0.04,
            created_at=datetime.utcnow()
        )
        db.add(biz)
    
    db.commit()
    return {"sku": sku, "asin": asin}


class TestAdsAnalysisService:
    """AdsAnalysisService 测试套件"""
    
    def test_verify_store_access_success(self, db: Session, test_user: User, test_store: AmazonStore):
        """测试店铺权限验证 - 成功场景"""
        store = AdsAnalysisService.verify_store_access(db, test_store.id, test_user.id)
        assert store.id == test_store.id
        assert store.user_id == test_user.id
    
    def test_verify_store_access_wrong_user(self, db: Session, test_store: AmazonStore):
        """测试店铺权限验证 - 错误用户"""
        wrong_user_id = 99999
        with pytest.raises(HTTPException) as exc_info:
            AdsAnalysisService.verify_store_access(db, test_store.id, wrong_user_id)
        assert exc_info.value.status_code == 404
        assert "not found or access denied" in str(exc_info.value.detail)
    
    def test_verify_store_access_nonexistent_store(self, db: Session, test_user: User):
        """测试店铺权限验证 - 不存在的店铺"""
        fake_store_id = uuid4()
        with pytest.raises(HTTPException) as exc_info:
            AdsAnalysisService.verify_store_access(db, fake_store_id, test_user.id)
        assert exc_info.value.status_code == 404
    
    def test_get_user_stores(self, db: Session, test_user: User, test_store: AmazonStore):
        """测试获取用户店铺列表"""
        stores = AdsAnalysisService.get_user_stores(db, test_user.id)
        assert len(stores) >= 1
        assert any(s.id == test_store.id for s in stores)
        assert all(s.user_id == test_user.id for s in stores)
        assert all(s.is_active for s in stores)
    
    def test_get_user_stores_empty(self, db: Session):
        """测试获取空店铺列表"""
        nonexistent_user_id = 99999
        stores = AdsAnalysisService.get_user_stores(db, nonexistent_user_id)
        assert len(stores) == 0
    
    def test_get_matrix_data(
        self, 
        db: Session, 
        test_user: User, 
        test_store: AmazonStore, 
        test_sku_data: dict
    ):
        """测试获取矩阵数据"""
        matrix_data = AdsAnalysisService.get_matrix_data(
            db=db,
            store_id=test_store.id,
            user_id=test_user.id,
            days=30
        )
        
        assert len(matrix_data) >= 1
        
        # 验证数据结构
        point = matrix_data[0]
        assert point.sku == test_sku_data["sku"]
        assert point.asin == test_sku_data["asin"]
        assert point.stock_weeks > 0
        assert point.tacos >= 0
        assert point.sales > 0
        assert point.status in [
            "CRITICAL / CLEARANCE",
            "STAR / GROWTH",
            "POTENTIAL / DEFENSE",
            "DROP / KILL"
        ]
    
    def test_get_matrix_data_wrong_user(
        self, 
        db: Session, 
        test_store: AmazonStore, 
        test_sku_data: dict
    ):
        """测试获取矩阵数据 - 错误用户"""
        wrong_user_id = 99999
        with pytest.raises(HTTPException) as exc_info:
            AdsAnalysisService.get_matrix_data(
                db=db,
                store_id=test_store.id,
                user_id=wrong_user_id,
                days=30
            )
        assert exc_info.value.status_code == 404
    
    def test_classify_sku_critical(self):
        """测试 SKU 分类 - Critical"""
        status = AdsAnalysisService._classify_sku(weeks_of_cover=30, tacos=25)
        assert status == "CRITICAL / CLEARANCE"
    
    def test_classify_sku_star(self):
        """测试 SKU 分类 - Star"""
        status = AdsAnalysisService._classify_sku(weeks_of_cover=30, tacos=15)
        assert status == "STAR / GROWTH"
    
    def test_classify_sku_potential(self):
        """测试 SKU 分类 - Potential"""
        status = AdsAnalysisService._classify_sku(weeks_of_cover=20, tacos=15)
        assert status == "POTENTIAL / DEFENSE"
    
    def test_classify_sku_drop(self):
        """测试 SKU 分类 - Drop"""
        status = AdsAnalysisService._classify_sku(weeks_of_cover=20, tacos=25)
        assert status == "DROP / KILL"
    
    def test_classify_sku_boundary_conditions(self):
        """测试 SKU 分类 - 边界条件"""
        # 边界值: 24 周, 20% TACOS
        assert AdsAnalysisService._classify_sku(24.1, 20.1) == "CRITICAL / CLEARANCE"
        assert AdsAnalysisService._classify_sku(24.1, 20.0) == "STAR / GROWTH"
        assert AdsAnalysisService._classify_sku(24.0, 20.0) == "POTENTIAL / DEFENSE"
        assert AdsAnalysisService._classify_sku(24.0, 20.1) == "DROP / KILL"
    
    def test_generate_diagnosis_critical(self):
        """测试生成诊断 - Critical"""
        from app.schemas.amazon_ads import AdsMatrixPoint
        
        point = AdsMatrixPoint(
            sku="TEST-SKU",
            asin="B00TEST",
            stock_weeks=30.0,
            tacos=25.0,
            sales=1000.0,
            status="CRITICAL / CLEARANCE",
            inventory_qty=1000,
            ad_spend=250.0,
            total_sales=1000.0,
            ctr=0.5,
            cvr=10.0,
            acos=25.0,
            roas=4.0,
            margin=15.0
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU", point)
        assert "紧急清仓" in diagnosis
        assert "TEST-SKU" in diagnosis
        assert "降低售价" in diagnosis
    
    def test_generate_diagnosis_star(self):
        """测试生成诊断 - Star"""
        from app.schemas.amazon_ads import AdsMatrixPoint
        
        point = AdsMatrixPoint(
            sku="TEST-SKU",
            asin="B00TEST",
            stock_weeks=30.0,
            tacos=15.0,
            sales=1000.0,
            status="STAR / GROWTH",
            inventory_qty=1000,
            ad_spend=150.0,
            total_sales=1000.0,
            ctr=1.2,
            cvr=15.0,
            acos=15.0,
            roas=6.6,
            margin=25.0
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU", point)
        assert "霸屏增长" in diagnosis
        assert "TEST-SKU" in diagnosis
        assert "提高核心关键词竞价" in diagnosis
    
    def test_generate_diagnosis_potential(self):
        """测试生成诊断 - Potential"""
        from app.schemas.amazon_ads import AdsMatrixPoint
        
        point = AdsMatrixPoint(
            sku="TEST-SKU",
            asin="B00TEST",
            stock_weeks=20.0,
            tacos=15.0,
            sales=1000.0,
            status="POTENTIAL / DEFENSE",
            inventory_qty=500,
            ad_spend=150.0,
            total_sales=1000.0,
            ctr=0.8,
            cvr=12.0,
            acos=15.0,
            roas=6.6,
            margin=10.0
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU", point)
        assert "防守控量" in diagnosis
        assert "TEST-SKU" in diagnosis
        assert "降低预算" in diagnosis
    
    def test_generate_diagnosis_drop(self):
        """测试生成诊断 - Drop"""
        from app.schemas.amazon_ads import AdsMatrixPoint
        
        point = AdsMatrixPoint(
            sku="TEST-SKU",
            asin="B00TEST",
            stock_weeks=20.0,
            tacos=25.0,
            sales=100.0,
            status="DROP / KILL",
            inventory_qty=500,
            ad_spend=25.0,
            total_sales=100.0,
            ctr=0.3,
            cvr=5.0,
            acos=25.0,
            roas=4.0,
            margin=-5.0
        )
        
        diagnosis = AdsAnalysisService.generate_diagnosis("TEST-SKU", point)
        assert "考虑淘汰" in diagnosis
        assert "TEST-SKU" in diagnosis
        assert "减少广告投入" in diagnosis


class TestMetricsCalculation:
    """指标计算测试"""
    
    def test_tacos_calculation(
        self, 
        db: Session, 
        test_user: User, 
        test_store: AmazonStore, 
        test_sku_data: dict
    ):
        """测试 TACOS 计算准确性"""
        matrix_data = AdsAnalysisService.get_matrix_data(
            db=db,
            store_id=test_store.id,
            user_id=test_user.id,
            days=30
        )
        
        point = matrix_data[0]
        
        # 验证 TACOS 计算
        # TACOS = (总广告花费 / 总销售额) * 100
        # 根据 test_sku_data: spend=50*30=1500, total_sales=300*30=9000
        # TACOS = 1500 / 9000 * 100 = 16.67%
        expected_tacos = (50.0 * 30) / (300.0 * 30) * 100
        assert abs(point.tacos - expected_tacos) < 0.1
    
    def test_weeks_of_cover_calculation(
        self, 
        db: Session, 
        test_user: User, 
        test_store: AmazonStore, 
        test_sku_data: dict
    ):
        """测试库存周转计算准确性"""
        matrix_data = AdsAnalysisService.get_matrix_data(
            db=db,
            store_id=test_store.id,
            user_id=test_user.id,
            days=30
        )
        
        point = matrix_data[0]
        
        # 验证库存周转计算
        # 当前库存 = 1000 (最新)
        # 日均销量 = 20 (total_units_ordered)
        # Weeks of Cover = 1000 / (20 * 7) = 7.14 周
        current_stock = 1000
        avg_daily_units = 20
        expected_weeks = current_stock / (avg_daily_units * 7)
        
        assert abs(point.stock_weeks - expected_weeks) < 0.5


class TestEdgeCases:
    """边界情况测试"""
    
    def test_zero_sales(self, db: Session, test_user: User, test_store: AmazonStore):
        """测试零销量场景"""
        today = date.today()
        sku = "ZERO-SALES-SKU"
        
        # 创建零销量数据
        for i in range(30):
            snapshot_date = today - timedelta(days=i)
            
            inv = InventorySnapshot(
                id=uuid4(),
                store_id=test_store.id,
                date=snapshot_date,
                sku=sku,
                asin="B00ZERO",
                fba_inventory=1000,
                inbound_inventory=0,
                reserved_inventory=0,
                unfulfillable_inventory=0,
                created_at=datetime.utcnow()
            )
            db.add(inv)
            
            biz = BusinessMetricSnapshot(
                id=uuid4(),
                store_id=test_store.id,
                date=snapshot_date,
                sku=sku,
                asin="B00ZERO",
                total_sales_amount=0.0,
                total_units_ordered=0,
                sessions=0,
                page_views=0,
                created_at=datetime.utcnow()
            )
            db.add(biz)
        
        db.commit()
        
        matrix_data = AdsAnalysisService.get_matrix_data(
            db=db,
            store_id=test_store.id,
            user_id=test_user.id,
            days=30
        )
        
        # 应该能处理零销量，库存周转应该被 cap 到 52
        zero_sales_point = next((p for p in matrix_data if p.sku == sku), None)
        if zero_sales_point:
            assert zero_sales_point.stock_weeks == 52.0
    
    def test_no_inventory(self, db: Session, test_user: User, test_store: AmazonStore):
        """测试零库存场景"""
        today = date.today()
        sku = "NO-INV-SKU"
        
        # 创建零库存但有销量的数据
        inv = InventorySnapshot(
            id=uuid4(),
            store_id=test_store.id,
            date=today,
            sku=sku,
            asin="B00NOINV",
            fba_inventory=0,
            inbound_inventory=0,
            reserved_inventory=0,
            unfulfillable_inventory=0,
            created_at=datetime.utcnow()
        )
        db.add(inv)
        
        for i in range(30):
            snapshot_date = today - timedelta(days=i)
            biz = BusinessMetricSnapshot(
                id=uuid4(),
                store_id=test_store.id,
                date=snapshot_date,
                sku=sku,
                asin="B00NOINV",
                total_sales_amount=100.0,
                total_units_ordered=5,
                sessions=100,
                page_views=150,
                created_at=datetime.utcnow()
            )
            db.add(biz)
        
        db.commit()
        
        matrix_data = AdsAnalysisService.get_matrix_data(
            db=db,
            store_id=test_store.id,
            user_id=test_user.id,
            days=30
        )
        
        # 零库存应该显示为 0 周
        no_inv_point = next((p for p in matrix_data if p.sku == sku), None)
        if no_inv_point:
            assert no_inv_point.stock_weeks == 0.0
