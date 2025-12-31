from typing import Any, List, Optional
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from app.api import deps
from app.models.amazon_ads import AdvertisingCampaign, CampaignPerformanceSnapshot, AmazonStore
from app.schemas.amazon_ads import CampaignListResponse, CampaignDetail

router = APIRouter()

@router.get("/campaigns", response_model=CampaignListResponse)
def get_campaigns(
    *,
    db: Session = Depends(deps.get_db),
    store_id: Optional[UUID] = None,
    state: Optional[str] = None,
    campaign_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "spend",
    sort_order: str = "desc"
) -> Any:
    """
    获取广告活动列表，包含聚合的表现数据 (Spend, Sales, ACOS, etc.)
    """
    # 默认时间范围：过去 30 天
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # 1. 构建基础查询
    query = db.query(
        AdvertisingCampaign,
        func.sum(CampaignPerformanceSnapshot.impressions).label("impressions"),
        func.sum(CampaignPerformanceSnapshot.clicks).label("clicks"),
        func.sum(CampaignPerformanceSnapshot.spend).label("spend"),
        func.sum(CampaignPerformanceSnapshot.sales).label("sales"),
        func.sum(CampaignPerformanceSnapshot.orders).label("orders"),
        func.sum(CampaignPerformanceSnapshot.units).label("units")
    ).outerjoin(
        CampaignPerformanceSnapshot,
        (AdvertisingCampaign.id == CampaignPerformanceSnapshot.campaign_id) &
        (CampaignPerformanceSnapshot.date >= start_date) &
        (CampaignPerformanceSnapshot.date <= end_date)
    )

    # 2. 应用筛选
    if store_id:
        query = query.filter(AdvertisingCampaign.store_id == store_id)
    if state:
        query = query.filter(AdvertisingCampaign.state == state)
    if campaign_type:
        query = query.filter(AdvertisingCampaign.campaign_type == campaign_type)

    # 3. 分组
    query = query.group_by(AdvertisingCampaign.id)

    # 4. 排序 (需要根据聚合字段排序，比较复杂，这里先在内存中排序或简化处理)
    # 为了性能，最好在 SQL 层排序。SQLAlchemy 的 label 可以用于 order_by
    if sort_order == "desc":
        query = query.order_by(desc(sort_by))
    else:
        query = query.order_by(asc(sort_by))

    # 5. 分页
    total = query.count()
    campaigns_data = query.offset((page - 1) * limit).limit(limit).all()

    # 6. 格式化输出
    results = []
    for camp, imp, clicks, spend, sales, orders, units in campaigns_data:
        # 处理 None 值
        imp = imp or 0
        clicks = clicks or 0
        spend = spend or 0.0
        sales = sales or 0.0
        orders = orders or 0
        units = units or 0
        
        # 计算衍生指标
        ctr = (clicks / imp * 100) if imp > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0
        acos = (spend / sales * 100) if sales > 0 else 0.0
        roas = (sales / spend) if spend > 0 else 0.0
        cvr = (orders / clicks * 100) if clicks > 0 else 0.0

        results.append({
            "id": camp.id,
            "campaign_id": camp.campaign_id, # Amazon ID
            "name": camp.name,
            "state": camp.state,
            "campaign_type": camp.campaign_type,
            "targeting_type": camp.targeting_type,
            "daily_budget": camp.daily_budget,
            "start_date": camp.start_date,
            "end_date": camp.end_date,
            # Metrics
            "impressions": imp,
            "clicks": clicks,
            "spend": round(spend, 2),
            "sales": round(sales, 2),
            "orders": orders,
            "units": units,
            "ctr": round(ctr, 2),
            "cpc": round(cpc, 2),
            "acos": round(acos, 2),
            "roas": round(roas, 2),
            "cvr": round(cvr, 2)
        })

    return {
        "total": total,
        "items": results,
        "page": page,
        "limit": limit
    }
