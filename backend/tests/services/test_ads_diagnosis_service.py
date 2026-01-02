import pytest
from datetime import date, timedelta
from uuid import uuid4
from app.services.ads_diagnosis_service import ads_diagnosis_service
from app.models.amazon_ads import AdvertisingCampaign, CampaignPerformanceSnapshot

# Mock 数据辅助函数
def create_campaign(db, store_id, name, state='enabled'):
    campaign = AdvertisingCampaign(
        id=str(uuid4()),
        store_id=store_id,
        name=name,
        state=state,
        daily_budget=10.0,
        targeting_type='MANUAL'
    )
    db.add(campaign)
    db.commit()
    return campaign

def create_snapshot(db, campaign_id, days_ago, spend, sales, orders, clicks=10):
    snapshot = CampaignPerformanceSnapshot(
        id=str(uuid4()),
        campaign_id=campaign_id,
        date=date.today() - timedelta(days=days_ago),
        impressions=1000,
        clicks=clicks,
        spend=spend,
        sales=sales,
        orders=orders
    )
    db.add(snapshot)
    db.commit()
    return snapshot

def test_check_wasted_spend(db_session):
    store_id = uuid4()
    
    # 1. 目标：花费 $60, 0 单 -> 应该被抓出来 (阈值 $50)
    c1 = create_campaign(db_session, store_id, "Wasted Campaign")
    create_snapshot(db_session, c1.id, 1, 60.0, 0.0, 0)
    
    # 2. 对照组：花费 $40, 0 单 -> 不应被抓出来 (未达阈值)
    c2 = create_campaign(db_session, store_id, "Low Spend Campaign")
    create_snapshot(db_session, c2.id, 1, 40.0, 0.0, 0)
    
    # 3. 对照组：花费 $100, 1 单 -> 不应被抓出来 (有转化)
    c3 = create_campaign(db_session, store_id, "Good Campaign")
    create_snapshot(db_session, c3.id, 1, 100.0, 50.0, 1)
    
    # 执行诊断
    result = ads_diagnosis_service.check_wasted_spend(db_session, store_id, days=7, threshold=50.0)
    
    assert result['campaign_count'] == 1
    assert result['total_wasted_spend'] == 60.0
    assert result['campaigns'][0]['id'] == c1.id
    assert result['campaigns'][0]['name'] == "Wasted Campaign"

def test_check_high_acos(db_session):
    store_id = uuid4()
    
    # 1. 目标：花费 $100, 销售 $200 -> ACOS 50% -> 应该被抓出来 (阈值 30%)
    c1 = create_campaign(db_session, store_id, "High ACOS Campaign")
    create_snapshot(db_session, c1.id, 1, 100.0, 200.0, 5)
    
    # 2. 对照组：花费 $20, 销售 $100 -> ACOS 20% -> 不应被抓出来
    c2 = create_campaign(db_session, store_id, "Good ACOS Campaign")
    create_snapshot(db_session, c2.id, 1, 20.0, 100.0, 5)
    
    # 3. 边界组：花费 $100, 销售 $0 -> ACOS 无穷大 -> 不应在此处处理 (这是 Wasted Spend 的职责)
    # 注意：check_high_acos 的 SQL 逻辑通常会过滤掉 sales=0 的记录，或者我们在代码里过滤
    c3 = create_campaign(db_session, store_id, "Zero Sales Campaign")
    create_snapshot(db_session, c3.id, 1, 100.0, 0.0, 0)
    
    # 执行诊断
    result = ads_diagnosis_service.check_high_acos(db_session, store_id, days=7, acos_threshold=30.0, min_spend=10.0)
    
    # 验证
    # c1 应该在列表里
    campaign_ids = [c['id'] for c in result['campaigns']]
    assert c1.id in campaign_ids
    assert c2.id not in campaign_ids
    
    # 验证 c3 是否被过滤 (取决于实现逻辑，通常 ACOS 计算需要 sales > 0)
    # 我们的实现中有 (func.sum(CampaignPerformanceSnapshot.sales) > 0) 的 having 子句
    assert c3.id not in campaign_ids

def test_empty_data_resilience(db_session):
    """测试无数据时的健壮性"""
    store_id = uuid4()
    
    # 无效花费检查
    res_wasted = ads_diagnosis_service.check_wasted_spend(db_session, store_id)
    assert res_wasted['campaign_count'] == 0
    assert res_wasted['total_wasted_spend'] == 0.0
    assert res_wasted['campaigns'] == []
    
    # 高 ACOS 检查
    res_acos = ads_diagnosis_service.check_high_acos(db_session, store_id)
    assert res_acos['campaign_count'] == 0
    assert res_acos['campaigns'] == []
