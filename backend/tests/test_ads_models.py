"""
Amazon Ads 数据模型测试
测试所有数据模型的约束、关系和验证
"""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.amazon_ads import (
    AmazonStore,
    ProductCost,
    InventorySnapshot,
    AdsMetricSnapshot,
    BusinessMetricSnapshot
)
from app.models.user import User


@pytest.fixture
def test_user(db: Session):
    """创建测试用户"""
    user = User(
        username="model_test_user",
        email="model_test@example.com",
        hashed_password="hashed",
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestAmazonStoreModel:
    """AmazonStore 模型测试"""
    
    def test_create_store(self, db: Session, test_user: User):
        """测试创建店铺"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST123",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        db.refresh(store)
        
        assert store.id is not None
        assert store.user_id == test_user.id
        assert store.store_name == "Test Store"
        assert store.is_active is True
    
    def test_store_unique_constraint(self, db: Session, test_user: User):
        """测试店铺唯一约束"""
        store1 = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Store 1",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="SAME_SELLER",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store1)
        db.commit()
        
        # 尝试创建相同的 user_id + marketplace_id + seller_id
        store2 = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Store 2",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="SAME_SELLER",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store2)
        
        with pytest.raises(IntegrityError):
            db.commit()
    
    def test_store_foreign_key(self, db: Session):
        """测试店铺外键约束"""
        store = AmazonStore(
            id=uuid4(),
            user_id=99999,  # 不存在的用户
            store_name="Invalid Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        
        with pytest.raises(IntegrityError):
            db.commit()


class TestProductCostModel:
    """ProductCost 模型测试"""
    
    def test_create_product_cost(self, db: Session, test_user: User):
        """测试创建产品成本"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        cost = ProductCost(
            id=uuid4(),
            store_id=store.id,
            sku="TEST-SKU",
            asin="B00TEST",
            cogs=10.50,
            currency="USD",
            fba_fee=3.00,
            referral_fee_rate=0.15,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(cost)
        db.commit()
        db.refresh(cost)
        
        assert cost.sku == "TEST-SKU"
        assert cost.cogs == 10.50
        assert cost.currency == "USD"
    
    def test_product_cost_unique_constraint(self, db: Session, test_user: User):
        """测试产品成本唯一约束"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        cost1 = ProductCost(
            id=uuid4(),
            store_id=store.id,
            sku="SAME-SKU",
            asin="B00TEST1",
            cogs=10.0,
            currency="USD",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(cost1)
        db.commit()
        
        # 尝试创建相同的 store_id + sku
        cost2 = ProductCost(
            id=uuid4(),
            store_id=store.id,
            sku="SAME-SKU",
            asin="B00TEST2",
            cogs=15.0,
            currency="USD",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(cost2)
        
        with pytest.raises(IntegrityError):
            db.commit()


class TestInventorySnapshotModel:
    """InventorySnapshot 模型测试"""
    
    def test_create_inventory_snapshot(self, db: Session, test_user: User):
        """测试创建库存快照"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        snapshot = InventorySnapshot(
            id=uuid4(),
            store_id=store.id,
            date=date.today(),
            sku="TEST-SKU",
            asin="B00TEST",
            fba_inventory=1000,
            inbound_inventory=200,
            reserved_inventory=50,
            unfulfillable_inventory=10,
            created_at=datetime.utcnow()
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        assert snapshot.fba_inventory == 1000
        assert snapshot.inbound_inventory == 200
    
    def test_inventory_snapshot_unique_constraint(self, db: Session, test_user: User):
        """测试库存快照唯一约束"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        today = date.today()
        
        snapshot1 = InventorySnapshot(
            id=uuid4(),
            store_id=store.id,
            date=today,
            sku="SAME-SKU",
            asin="B00TEST",
            fba_inventory=1000,
            inbound_inventory=0,
            reserved_inventory=0,
            unfulfillable_inventory=0,
            created_at=datetime.utcnow()
        )
        db.add(snapshot1)
        db.commit()
        
        # 尝试创建相同的 store_id + date + sku
        snapshot2 = InventorySnapshot(
            id=uuid4(),
            store_id=store.id,
            date=today,
            sku="SAME-SKU",
            asin="B00TEST",
            fba_inventory=2000,
            inbound_inventory=0,
            reserved_inventory=0,
            unfulfillable_inventory=0,
            created_at=datetime.utcnow()
        )
        db.add(snapshot2)
        
        with pytest.raises(IntegrityError):
            db.commit()


class TestAdsMetricSnapshotModel:
    """AdsMetricSnapshot 模型测试"""
    
    def test_create_ads_snapshot(self, db: Session, test_user: User):
        """测试创建广告快照"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        snapshot = AdsMetricSnapshot(
            id=uuid4(),
            store_id=store.id,
            date=date.today(),
            sku="TEST-SKU",
            asin="B00TEST",
            spend=50.0,
            sales=200.0,
            impressions=10000,
            clicks=100,
            orders=10,
            units=15,
            created_at=datetime.utcnow()
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        assert snapshot.spend == 50.0
        assert snapshot.sales == 200.0
        assert snapshot.clicks == 100


class TestBusinessMetricSnapshotModel:
    """BusinessMetricSnapshot 模型测试"""
    
    def test_create_business_snapshot(self, db: Session, test_user: User):
        """测试创建业务快照"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        snapshot = BusinessMetricSnapshot(
            id=uuid4(),
            store_id=store.id,
            date=date.today(),
            sku="TEST-SKU",
            asin="B00TEST",
            total_sales_amount=300.0,
            total_units_ordered=20,
            sessions=500,
            page_views=800,
            unit_session_percentage=0.04,
            created_at=datetime.utcnow()
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        assert snapshot.total_sales_amount == 300.0
        assert snapshot.total_units_ordered == 20
        assert snapshot.unit_session_percentage == 0.04


class TestCascadeDelete:
    """级联删除测试"""
    
    def test_delete_store_cascades_to_costs(self, db: Session, test_user: User):
        """测试删除店铺时级联删除成本"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        cost = ProductCost(
            id=uuid4(),
            store_id=store.id,
            sku="TEST-SKU",
            asin="B00TEST",
            cogs=10.0,
            currency="USD",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(cost)
        db.commit()
        
        cost_id = cost.id
        
        # 删除店铺
        db.delete(store)
        db.commit()
        
        # 验证成本也被删除
        deleted_cost = db.query(ProductCost).filter(ProductCost.id == cost_id).first()
        assert deleted_cost is None
    
    def test_delete_store_cascades_to_snapshots(self, db: Session, test_user: User):
        """测试删除店铺时级联删除快照"""
        store = AmazonStore(
            id=uuid4(),
            user_id=test_user.id,
            store_name="Test Store",
            marketplace_id="ATVPDKIKX0DER",
            marketplace_name="United States",
            seller_id="TEST",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        
        # 创建各种快照
        inv = InventorySnapshot(
            id=uuid4(),
            store_id=store.id,
            date=date.today(),
            sku="TEST-SKU",
            asin="B00TEST",
            fba_inventory=1000,
            inbound_inventory=0,
            reserved_inventory=0,
            unfulfillable_inventory=0,
            created_at=datetime.utcnow()
        )
        db.add(inv)
        
        ads = AdsMetricSnapshot(
            id=uuid4(),
            store_id=store.id,
            date=date.today(),
            sku="TEST-SKU",
            asin="B00TEST",
            spend=50.0,
            sales=200.0,
            impressions=1000,
            clicks=10,
            orders=5,
            units=8,
            created_at=datetime.utcnow()
        )
        db.add(ads)
        
        biz = BusinessMetricSnapshot(
            id=uuid4(),
            store_id=store.id,
            date=date.today(),
            sku="TEST-SKU",
            asin="B00TEST",
            total_sales_amount=300.0,
            total_units_ordered=20,
            sessions=500,
            page_views=800,
            created_at=datetime.utcnow()
        )
        db.add(biz)
        db.commit()
        
        inv_id = inv.id
        ads_id = ads.id
        biz_id = biz.id
        
        # 删除店铺
        db.delete(store)
        db.commit()
        
        # 验证所有快照都被删除
        assert db.query(InventorySnapshot).filter(InventorySnapshot.id == inv_id).first() is None
        assert db.query(AdsMetricSnapshot).filter(AdsMetricSnapshot.id == ads_id).first() is None
        assert db.query(BusinessMetricSnapshot).filter(BusinessMetricSnapshot.id == biz_id).first() is None
