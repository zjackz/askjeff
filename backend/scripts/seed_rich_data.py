import sys
import os
import random
import math
from datetime import datetime, timedelta, date
from uuid import uuid4

# 添加 backend 目录到路径
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db import SessionLocal
from app.models.user import User
from app.models.amazon_ads import (
    AmazonStore, 
    ProductCost, 
    InventorySnapshot, 
    BusinessMetricSnapshot, 
    AdsMetricSnapshot,
    SyncTask,
    AdvertisingCampaign,
    AdvertisingAdGroup,
    CampaignPerformanceSnapshot
)

# 产品库定义
PRODUCTS = [
    # 电子产品 (高客单, 竞争激烈)
    {"sku": "ELEC-HEADPHONE-001", "asin": "B08XYZ1234", "name": "Active Noise Cancelling Headphones", "price": 89.99, "cogs": 35.00, "category": "Electronics", "lifecycle": "MATURE"},
    {"sku": "ELEC-CHARGER-USB-C", "asin": "B09ABC5678", "name": "65W GaN USB-C Charger", "price": 29.99, "cogs": 8.50, "category": "Electronics", "lifecycle": "GROWTH"},
    {"sku": "ELEC-CABLE-3PACK", "asin": "B07DEF9012", "name": "USB-C Cable 3-Pack 6ft", "price": 14.99, "cogs": 3.20, "category": "Electronics", "lifecycle": "MATURE"},
    {"sku": "ELEC-WEBCAM-HD", "asin": "B08GHI3456", "name": "1080p HD Webcam with Microphone", "price": 45.99, "cogs": 18.00, "category": "Electronics", "lifecycle": "DECLINE"},
    
    # 家居用品 (中客单, 流量稳定)
    {"sku": "HOME-COFFEE-MAKER", "asin": "B09JKL7890", "name": "Programmable Coffee Maker 12-Cup", "price": 59.99, "cogs": 22.00, "category": "Home", "lifecycle": "MATURE"},
    {"sku": "HOME-AIR-PURIFIER", "asin": "B08MNO1234", "name": "HEPA Air Purifier for Bedroom", "price": 129.99, "cogs": 45.00, "category": "Home", "lifecycle": "GROWTH"},
    {"sku": "HOME-PILLOW-MEM", "asin": "B07PQR5678", "name": "Memory Foam Pillow Queen Size", "price": 39.99, "cogs": 12.00, "category": "Home", "lifecycle": "MATURE"},
    {"sku": "HOME-KITCHEN-SCALE", "asin": "B09STU9012", "name": "Digital Kitchen Scale", "price": 12.99, "cogs": 4.50, "category": "Home", "lifecycle": "MATURE"},
    
    # 运动户外 (季节性, 波动大)
    {"sku": "SPORT-YOGA-MAT", "asin": "B08VWX3456", "name": "Non-Slip Yoga Mat 6mm", "price": 24.99, "cogs": 8.00, "category": "Sports", "lifecycle": "MATURE"},
    {"sku": "SPORT-DUMBBELL-SET", "asin": "B09YZA7890", "name": "Adjustable Dumbbell Set 50lbs", "price": 199.99, "cogs": 80.00, "category": "Sports", "lifecycle": "GROWTH"},
    {"sku": "SPORT-WATER-BOTTLE", "asin": "B07BCD1234", "name": "Insulated Water Bottle 32oz", "price": 19.99, "cogs": 6.00, "category": "Sports", "lifecycle": "MATURE"},
    {"sku": "SPORT-RESIST-BANDS", "asin": "B08EFG5678", "name": "Resistance Bands Set 5-Piece", "price": 15.99, "cogs": 4.00, "category": "Sports", "lifecycle": "DECLINE"},
    
    # 宠物用品 (高复购)
    {"sku": "PET-DOG-BED-L", "asin": "B09HIJ9012", "name": "Orthopedic Dog Bed Large", "price": 69.99, "cogs": 25.00, "category": "Pets", "lifecycle": "MATURE"},
    {"sku": "PET-CAT-TOY-LASER", "asin": "B08KLM3456", "name": "Interactive Laser Cat Toy", "price": 18.99, "cogs": 5.50, "category": "Pets", "lifecycle": "GROWTH"},
    {"sku": "PET-POOP-BAGS", "asin": "B07NOP7890", "name": "Dog Poop Bags 270 Count", "price": 13.99, "cogs": 4.00, "category": "Pets", "lifecycle": "MATURE"},
    
    # 新品 (测试期)
    {"sku": "NEW-SMART-WATCH", "asin": "B09QRS1234", "name": "Smart Watch Fitness Tracker 2024", "price": 49.99, "cogs": 20.00, "category": "Electronics", "lifecycle": "LAUNCH"},
    {"sku": "NEW-LED-STRIP", "asin": "B08TUV5678", "name": "RGB LED Strip Lights 50ft", "price": 22.99, "cogs": 9.00, "category": "Home", "lifecycle": "LAUNCH"},
]

def get_random_factor(base=1.0, variance=0.2):
    """获取随机波动因子"""
    return base + random.uniform(-variance, variance)

def is_weekend(d: date):
    """判断是否周末"""
    return d.weekday() >= 5

# 站点配置
MARKETS = [
    {
        "country_code": "US",
        "marketplace_id": "ATVPDKIKX0DER",
        "name": "Official Store (US)",
        "currency": "USD",
        "traffic_multiplier": 1.0,
        "price_multiplier": 1.0
    },
    {
        "country_code": "UK",
        "marketplace_id": "A1F83G8C2ARO7P",
        "name": "Official Store (UK)",
        "currency": "GBP",
        "traffic_multiplier": 0.3, # 流量约为美国的 30%
        "price_multiplier": 0.8 # 数值上价格较低 (1 USD != 1 GBP)
    },
    {
        "country_code": "DE",
        "marketplace_id": "A1PA6795UKMFR9",
        "name": "Official Store (DE)",
        "currency": "EUR",
        "traffic_multiplier": 0.4,
        "price_multiplier": 0.9
    }
]

def seed_rich_data():
    db = SessionLocal()
    try:
        print("🌱 开始生成多站点深度模拟数据 (含 Campaign & Refunds)...")
        
        # 1. 获取用户
        user = db.query(User).first()
        if not user:
            print("❌ 未找到用户，请先注册。")
            return

        for market in MARKETS:
            print(f"\n🌍 处理站点: {market['name']} ({market['currency']})")
            
            # 2. 获取或创建店铺
            store = db.query(AmazonStore).filter(
                AmazonStore.user_id == user.id,
                AmazonStore.marketplace_id == market['marketplace_id']
            ).first()
            
            if not store:
                print(f"  Creating new store for {market['country_code']}...")
                store = AmazonStore(
                    user_id=user.id,
                    store_name=market['name'],
                    seller_id=f"SELLER_TEST_{market['country_code']}",
                    marketplace_id=market['marketplace_id'],
                    marketplace_name=market['name'],
                    sp_api_refresh_token=f"mock_refresh_{market['country_code']}",
                    advertising_api_refresh_token=f"mock_ads_{market['country_code']}",
                    is_active=True
                )
                db.add(store)
                db.commit()
                db.refresh(store)
            
            # 3. 初始化产品成本 (ProductCost)
            print("  💰 初始化产品成本...")
            for p in PRODUCTS:
                cost = db.query(ProductCost).filter_by(store_id=store.id, sku=p['sku']).first()
                if not cost:
                    # 根据站点调整价格和成本
                    local_price = round(p['price'] * market['price_multiplier'], 2)
                    local_cogs = round(p['cogs'] * market['price_multiplier'], 2)
                    
                    cost = ProductCost(
                        store_id=store.id,
                        sku=p['sku'],
                        asin=p['asin'],
                        cogs=local_cogs,
                        currency=market['currency'],
                        fba_fee=local_price * 0.15 + 3.0,
                        referral_fee_rate=0.15
                    )
                    db.add(cost)
            db.commit()

            # 3.5 初始化广告活动 (Campaigns & AdGroups)
            print("  📢 初始化广告活动...")
            campaigns_map = {} # sku -> {'auto': campaign_obj, 'manual': campaign_obj}
            
            for p in PRODUCTS:
                campaigns_map[p['sku']] = {}
                
                # Auto Campaign
                auto_camp_name = f"SP-Auto-{p['sku']}"
                auto_camp = db.query(AdvertisingCampaign).filter_by(store_id=store.id, name=auto_camp_name).first()
                if not auto_camp:
                    auto_camp = AdvertisingCampaign(
                        store_id=store.id,
                        campaign_id=f"CAMP-AUTO-{p['sku']}-{market['country_code']}",
                        name=auto_camp_name,
                        campaign_type="sponsoredProducts",
                        targeting_type="auto",
                        daily_budget=20.0,
                        state="enabled",
                        start_date=date.today() - timedelta(days=365)
                    )
                    db.add(auto_camp)
                    db.flush() # 获取 ID
                    
                    # AdGroup
                    ad_group = AdvertisingAdGroup(
                        store_id=store.id,
                        campaign_id=auto_camp.id,
                        ad_group_id=f"AG-AUTO-{p['sku']}-{market['country_code']}",
                        name=f"AG-Auto-{p['sku']}",
                        default_bid=0.5 * market['price_multiplier'],
                        state="enabled"
                    )
                    db.add(ad_group)
                campaigns_map[p['sku']]['auto'] = auto_camp
                
                # Manual Campaign
                manual_camp_name = f"SP-Manual-{p['sku']}"
                manual_camp = db.query(AdvertisingCampaign).filter_by(store_id=store.id, name=manual_camp_name).first()
                if not manual_camp:
                    manual_camp = AdvertisingCampaign(
                        store_id=store.id,
                        campaign_id=f"CAMP-MANUAL-{p['sku']}-{market['country_code']}",
                        name=manual_camp_name,
                        campaign_type="sponsoredProducts",
                        targeting_type="manual",
                        daily_budget=50.0,
                        state="enabled",
                        start_date=date.today() - timedelta(days=365)
                    )
                    db.add(manual_camp)
                    db.flush()
                    
                    # AdGroup
                    ad_group = AdvertisingAdGroup(
                        store_id=store.id,
                        campaign_id=manual_camp.id,
                        ad_group_id=f"AG-MANUAL-{p['sku']}-{market['country_code']}",
                        name=f"AG-Manual-{p['sku']}",
                        default_bid=1.2 * market['price_multiplier'],
                        state="enabled"
                    )
                    db.add(ad_group)
                campaigns_map[p['sku']]['manual'] = manual_camp
            
            db.commit()

            # 4. 生成过去 60 天的数据
            end_date = date.today()
            start_date = end_date - timedelta(days=60)
            current_date = start_date

            # 初始化库存
            inventory_levels = {p['sku']: random.randint(200, 1000) for p in PRODUCTS}

            print(f"  📅 生成数据范围: {start_date} 到 {end_date}")
            
            while current_date <= end_date:
                # print(f"    Processing {current_date}...", end='\r')
                
                # 模拟周末流量增加
                weekend_boost = 1.2 if is_weekend(current_date) else 1.0
                
                for p in PRODUCTS:
                    # --- 基础流量与销量 ---
                    # 根据生命周期设定基准流量
                    base_sessions = 0
                    if p['lifecycle'] == 'MATURE': base_sessions = 500
                    elif p['lifecycle'] == 'GROWTH': base_sessions = 800
                    elif p['lifecycle'] == 'DECLINE': base_sessions = 200
                    elif p['lifecycle'] == 'LAUNCH': base_sessions = 150
                    
                    # 站点流量调整
                    base_sessions = int(base_sessions * market['traffic_multiplier'])
                    
                    # 随机波动 + 周末效应
                    sessions = int(base_sessions * weekend_boost * get_random_factor(1.0, 0.3))
                    page_views = int(sessions * get_random_factor(1.5, 0.2))
                    
                    # 转化率 (CVR)
                    base_cvr = 0.05 # 5%
                    if p['category'] == 'Electronics': base_cvr = 0.03
                    if p['category'] == 'Pets': base_cvr = 0.08
                    
                    cvr = base_cvr * get_random_factor(1.0, 0.2)
                    total_units = int(sessions * cvr)
                    if total_units < 0: total_units = 0
                    
                    # 本地货币价格
                    local_price = round(p['price'] * market['price_multiplier'], 2)
                    total_sales = total_units * local_price
                    
                    # --- 退款数据 (新增) ---
                    # 模拟 3% - 8% 的退款率
                    refund_rate = random.uniform(0.03, 0.08)
                    # 假设退款有滞后，但为了简化，我们直接基于当天的销量计算一个“等效”退款量
                    refunded_units = int(total_units * refund_rate)
                    refunds = refunded_units * local_price
                    
                    # --- 广告表现 ---
                    # 广告占比 (TACOS 目标)
                    ads_share = 0.3 # 30% 的销量来自广告
                    if p['lifecycle'] == 'LAUNCH': ads_share = 0.8 # 新品主要靠广告
                    
                    ads_units = int(total_units * ads_share * get_random_factor(1.0, 0.2))
                    ads_sales = ads_units * local_price
                    
                    # 广告转化率通常略低于自然流量
                    ads_cvr = cvr * 0.9
                    if ads_cvr <= 0: ads_cvr = 0.01
                    
                    ads_clicks = int(ads_units / ads_cvr) if ads_cvr > 0 else 0
                    ads_impressions = int(ads_clicks * 150) # CTR ~ 0.6%
                    
                    # CPC (每次点击成本) - 根据站点调整
                    base_cpc = 1.2
                    if p['category'] == 'Electronics': base_cpc = 2.5
                    local_cpc = base_cpc * market['price_multiplier']
                    
                    ads_spend = ads_clicks * local_cpc
                    
                    # --- 分配广告数据到 Campaign ---
                    # 假设 Auto 占 40% 流量，转化差；Manual 占 60% 流量，转化好
                    auto_share = 0.4
                    
                    auto_clicks = int(ads_clicks * auto_share)
                    manual_clicks = ads_clicks - auto_clicks
                    
                    auto_spend = auto_clicks * (local_cpc * 0.7) # Auto CPC 较低
                    manual_spend = manual_clicks * (local_cpc * 1.2) # Manual CPC 较高
                    
                    auto_units = int(ads_units * 0.3) # Auto 转化较差
                    manual_units = ads_units - auto_units
                    
                    auto_sales = auto_units * local_price
                    manual_sales = manual_units * local_price
                    
                    auto_impressions = int(ads_impressions * 0.6) # Auto 曝光大
                    manual_impressions = ads_impressions - auto_impressions

                    # 写入 Campaign Performance
                    # Auto
                    auto_snap = db.query(CampaignPerformanceSnapshot).filter_by(
                        store_id=store.id, date=current_date, campaign_id=campaigns_map[p['sku']]['auto'].id
                    ).first()
                    if not auto_snap:
                        db.add(CampaignPerformanceSnapshot(
                            store_id=store.id,
                            campaign_id=campaigns_map[p['sku']]['auto'].id,
                            date=current_date,
                            impressions=auto_impressions,
                            clicks=auto_clicks,
                            spend=auto_spend,
                            sales=auto_sales,
                            orders=auto_units,
                            units=auto_units
                        ))
                        
                    # Manual
                    manual_snap = db.query(CampaignPerformanceSnapshot).filter_by(
                        store_id=store.id, date=current_date, campaign_id=campaigns_map[p['sku']]['manual'].id
                    ).first()
                    if not manual_snap:
                        db.add(CampaignPerformanceSnapshot(
                            store_id=store.id,
                            campaign_id=campaigns_map[p['sku']]['manual'].id,
                            date=current_date,
                            impressions=manual_impressions,
                            clicks=manual_clicks,
                            spend=manual_spend,
                            sales=manual_sales,
                            orders=manual_units,
                            units=manual_units
                        ))

                    # --- 库存逻辑 ---
                    inventory_levels[p['sku']] -= total_units
                    # 触发补货
                    if inventory_levels[p['sku']] < 100:
                        restock = random.randint(500, 1000)
                        inventory_levels[p['sku']] += restock
                        inbound = restock
                    else:
                        inbound = 0
                    
                    # --- 写入数据库 ---
                    
                    # 1. Business Metric
                    # 检查是否存在
                    biz_snap = db.query(BusinessMetricSnapshot).filter_by(store_id=store.id, date=current_date, sku=p['sku']).first()
                    if not biz_snap:
                        biz_snap = BusinessMetricSnapshot(
                            store_id=store.id,
                            date=current_date,
                            sku=p['sku'],
                            asin=p['asin'],
                            total_sales_amount=total_sales,
                            total_units_ordered=total_units,
                            sessions=sessions,
                            page_views=page_views,
                            unit_session_percentage=cvr * 100,
                            refunds=refunds, # 新增
                            refunded_units=refunded_units # 新增
                        )
                        db.add(biz_snap)
                    
                    # 2. Ads Metric
                    ads_snap = db.query(AdsMetricSnapshot).filter_by(store_id=store.id, date=current_date, sku=p['sku']).first()
                    if not ads_snap:
                        ads_snap = AdsMetricSnapshot(
                            store_id=store.id,
                            date=current_date,
                            sku=p['sku'],
                            asin=p['asin'],
                            spend=ads_spend,
                            sales=ads_sales,
                            impressions=ads_impressions,
                            clicks=ads_clicks,
                            orders=ads_units, # 简化假设 1 order = 1 unit
                            units=ads_units
                        )
                        db.add(ads_snap)
                    
                    # 3. Inventory Snapshot
                    inv_snap = db.query(InventorySnapshot).filter_by(store_id=store.id, date=current_date, sku=p['sku']).first()
                    if not inv_snap:
                        inv_snap = InventorySnapshot(
                            store_id=store.id,
                            date=current_date,
                            sku=p['sku'],
                            asin=p['asin'],
                            fba_inventory=max(0, inventory_levels[p['sku']]),
                            inbound_inventory=inbound,
                            reserved_inventory=int(total_units * 0.5), # 假设部分在处理中
                            unfulfillable_inventory=random.choice([0, 0, 0, 1, 2])
                        )
                        db.add(inv_snap)
                
                # 每天生成 3 条同步记录 (Inventory, Business, Ads)
                for sync_type in ['inventory', 'business', 'advertising']:
                    # 检查当天是否已有记录，避免重复
                    # 这里简单起见，只在没有记录时插入
                    # 为了不让 sync_tasks 表爆炸，我们只生成最近 7 天的详细记录
                    if (end_date - current_date).days < 7:
                        task_exists = db.query(SyncTask).filter(
                            SyncTask.store_id == store.id,
                            SyncTask.sync_type == sync_type,
                            SyncTask.created_at >= datetime.combine(current_date, datetime.min.time()),
                            SyncTask.created_at <= datetime.combine(current_date, datetime.max.time())
                        ).first()
                        
                        if not task_exists:
                            status = 'success'
                            # 模拟偶尔失败
                            if random.random() < 0.05: status = 'failed'
                            
                            task = SyncTask(
                                store_id=store.id,
                                sync_type=sync_type,
                                status=status,
                                start_time=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=2, minutes=random.randint(0, 59)),
                                end_time=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=2, minutes=random.randint(0, 59), seconds=random.randint(10, 120)),
                                records_synced=len(PRODUCTS) if status == 'success' else 0,
                                records_failed=0,
                                error_message="API Rate Limit Exceeded" if status == 'failed' else None,
                                created_at=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=3)
                            )
                            db.add(task)

                db.commit() # 每天提交一次
                current_date += timedelta(days=1)
            
        print("\n✅ 多站点深度模拟数据生成完成 (含 Campaign & Refunds)！")
        print(f"共生成 {len(MARKETS)} 个站点的 60 天历史数据。")
            
        print("\n✅ 深度模拟数据生成完成！")
        print(f"共生成 {len(PRODUCTS)} 个 SKU 的 60 天历史数据。")
        
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_rich_data()
