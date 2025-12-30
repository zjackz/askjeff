"""
多店铺 Mock 数据生成器
支持多用户、多店铺、多 SKU 的企业级数据模拟
"""
import random
import sys
import os
from datetime import date, datetime, timedelta
from uuid import uuid4

sys.path.append(os.getcwd())

from app.db import SessionLocal
from app.models.amazon_ads import (
    AmazonStore,
    ProductCost,
    InventorySnapshot,
    AdsMetricSnapshot,
    BusinessMetricSnapshot
)

# 市场配置
MARKETPLACES = [
    {"id": "ATVPDKIKX0DER", "name": "United States", "currency": "USD"},
    {"id": "A1PA6795UKMFR9", "name": "Germany", "currency": "EUR"},
    {"id": "A1F83G8C2ARO7P", "name": "United Kingdom", "currency": "GBP"},
    {"id": "A1VC38T7YXB528", "name": "Japan", "currency": "JPY"},
]

def generate_mock_data():
    db = SessionLocal()
    
    print("🗑️  清理旧数据...")
    db.query(BusinessMetricSnapshot).delete()
    db.query(AdsMetricSnapshot).delete()
    db.query(InventorySnapshot).delete()
    db.query(ProductCost).delete()
    db.query(AmazonStore).delete()
    db.commit()
    
    print("✅ 旧数据已清理")
    
    # 确保至少有一个用户
    from app.models.user import User
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        print("👤 创建默认管理员用户...")
        admin = User(
            username="admin",
            hashed_password="hashed_password", # 仅用于 mock
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    
    admin_user_id = admin.id
    
    # 创建 3 个店铺 (不同市场)
    stores = []
    for i, marketplace in enumerate(MARKETPLACES[:3]):  # 美国、德国、英国
        store = AmazonStore(
            id=uuid4(),
            user_id=admin_user_id,
            store_name=f"My {marketplace['name']} Store",
            marketplace_id=marketplace['id'],
            marketplace_name=marketplace['name'],
            seller_id=f"A{1000 + i}SELLER",
            is_active=True,
            last_sync_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        stores.append((store, marketplace))
    
    db.commit()
    print(f"✅ 创建了 {len(stores)} 个店铺")
    
    # 为每个店铺生成 SKU 和数据
    today = date.today()
    start_date = today - timedelta(days=30)
    
    total_skus = 0
    total_snapshots = 0
    
    for store, marketplace in stores:
        # 每个店铺 20-30 个 SKU
        num_skus = random.randint(20, 30)
        skus = []
        
        for i in range(num_skus):
            sku = f"{marketplace['id'][:2]}-SKU-{1000 + i}"
            asin = f"B{random.randint(100000, 999999)}"
            
            # 随机分配象限特征
            profile = random.choice(['critical', 'star', 'potential', 'drop', 'low_ctr', 'low_cvr'])
            
            if profile == 'critical':  # 高库存, 高 TACOS
                base_stock = random.randint(2000, 5000)
                base_sales = random.randint(10, 50)
                base_tacos = random.uniform(0.25, 0.50)
                ctr_range = (0.003, 0.006)
                cvr_range = (0.02, 0.05)
            elif profile == 'star':  # 高库存, 低 TACOS
                base_stock = random.randint(2000, 5000)
                base_sales = random.randint(100, 300)
                base_tacos = random.uniform(0.05, 0.15)
                ctr_range = (0.008, 0.015)
                cvr_range = (0.12, 0.20)
            elif profile == 'potential':  # 低库存, 低 TACOS
                base_stock = random.randint(100, 500)
                base_sales = random.randint(20, 80)
                base_tacos = random.uniform(0.10, 0.20)
                ctr_range = (0.005, 0.010)
                cvr_range = (0.08, 0.12)
            elif profile == 'low_ctr':  # 流量瓶颈 (低 CTR)
                base_stock = random.randint(500, 1000)
                base_sales = random.randint(10, 30)
                base_tacos = random.uniform(0.05, 0.10)
                ctr_range = (0.001, 0.003)
                cvr_range = (0.10, 0.15)
            elif profile == 'low_cvr':  # 转化瓶颈 (低 CVR)
                base_stock = random.randint(500, 1000)
                base_sales = random.randint(10, 30)
                base_tacos = random.uniform(0.30, 0.50)
                ctr_range = (0.008, 0.012)
                cvr_range = (0.01, 0.03)
            else:  # drop: 低库存, 高 TACOS
                base_stock = random.randint(50, 200)
                base_sales = random.randint(5, 20)
                base_tacos = random.uniform(0.30, 0.60)
                ctr_range = (0.003, 0.006)
                cvr_range = (0.03, 0.06)
            
            # 创建成本记录
            cogs = random.uniform(5.0, 20.0)
            cost = ProductCost(
                store_id=store.id,
                sku=sku,
                asin=asin,
                cogs=cogs,
                currency=marketplace['currency'],
                fba_fee=random.uniform(2.0, 5.0),
                referral_fee_rate=0.15,  # 15%
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(cost)
            skus.append((sku, asin, profile, base_stock, base_sales, base_tacos, ctr_range, cvr_range))
        
        total_skus += len(skus)
        
        # 生成每日快照
        for day_offset in range(31):
            current_date = start_date + timedelta(days=day_offset)
            
            for sku, asin, profile, base_stock, base_sales, base_tacos, ctr_range, cvr_range in skus:
                # 每日销量 (加噪声)
                daily_units = max(0, int(random.gauss(base_sales, base_sales * 0.2)))
                price = random.uniform(20.0, 50.0)
                daily_sales_amount = daily_units * price
                
                # 库存 (逐渐减少)
                current_stock = max(0, base_stock - (daily_units * day_offset // 7))
                
                # 广告数据
                ad_spend = daily_sales_amount * base_tacos * random.uniform(0.8, 1.2)
                
                # 基于 CTR 和 CVR 范围生成数据
                ctr = random.uniform(*ctr_range)
                cvr = random.uniform(*cvr_range)
                
                impressions = int(ad_spend * 1000 / 15)  # CPM $15
                clicks = int(impressions * ctr)
                orders = int(clicks * cvr)
                ad_sales = orders * price * random.uniform(0.9, 1.1)
                
                # 库存快照
                inv = InventorySnapshot(
                    store_id=store.id,
                    date=current_date,
                    sku=sku,
                    asin=asin,
                    fba_inventory=current_stock,
                    inbound_inventory=random.randint(0, 100),
                    reserved_inventory=random.randint(0, 50),
                    unfulfillable_inventory=random.randint(0, 10),
                    created_at=datetime.utcnow()
                )
                db.add(inv)
                
                # 广告快照
                ads = AdsMetricSnapshot(
                    store_id=store.id,
                    date=current_date,
                    sku=sku,
                    asin=asin,
                    spend=ad_spend,
                    sales=ad_sales,
                    impressions=impressions,
                    clicks=clicks,
                    orders=orders,
                    units=int(orders * random.uniform(1.0, 1.5)),
                    created_at=datetime.utcnow()
                )
                db.add(ads)
                
                # 业务快照
                biz = BusinessMetricSnapshot(
                    store_id=store.id,
                    date=current_date,
                    sku=sku,
                    asin=asin,
                    total_sales_amount=daily_sales_amount,
                    total_units_ordered=daily_units,
                    sessions=int(daily_units * 10),
                    page_views=int(daily_units * 15),
                    unit_session_percentage=random.uniform(0.05, 0.15),
                    created_at=datetime.utcnow()
                )
                db.add(biz)
                
                total_snapshots += 3
        
        print(f"  ✅ {store.store_name}: {len(skus)} SKUs, {len(skus) * 31 * 3} snapshots")
    
    db.commit()
    db.close()
    
    print(f"\n🎉 数据生成完成!")
    print(f"   - 店铺数: {len(stores)}")
    print(f"   - 总 SKU 数: {total_skus}")
    print(f"   - 总快照数: {total_snapshots}")

if __name__ == "__main__":
    generate_mock_data()
