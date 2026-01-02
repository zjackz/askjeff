from typing import List, Dict, Any
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.amazon_ads import AdvertisingCampaign, CampaignPerformanceSnapshot

class AdsDiagnosisService:
    @staticmethod
    def check_wasted_spend(db: Session, store_id: UUID, days: int = 7, threshold: float = 50.0) -> Dict[str, Any]:
        """
        检查无效花费：过去 N 天花费 > 阈值 且 订单 = 0 的广告活动
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 聚合查询
        results = db.query(
            AdvertisingCampaign.id,
            AdvertisingCampaign.name,
            func.sum(CampaignPerformanceSnapshot.spend).label("total_spend"),
            func.sum(CampaignPerformanceSnapshot.clicks).label("total_clicks"),
            func.sum(CampaignPerformanceSnapshot.orders).label("total_orders")
        ).join(
            CampaignPerformanceSnapshot,
            AdvertisingCampaign.id == CampaignPerformanceSnapshot.campaign_id
        ).filter(
            AdvertisingCampaign.store_id == store_id,
            CampaignPerformanceSnapshot.date >= start_date,
            CampaignPerformanceSnapshot.date <= end_date,
            AdvertisingCampaign.state == 'enabled' # 只检查开启的
        ).group_by(
            AdvertisingCampaign.id
        ).having(
            (func.sum(CampaignPerformanceSnapshot.spend) > threshold) &
            (func.sum(CampaignPerformanceSnapshot.orders) == 0)
        ).order_by(
            func.sum(CampaignPerformanceSnapshot.spend).desc()
        ).all()
        
        campaigns = []
        total_wasted = 0.0
        
        for r in results:
            spend = float(r.total_spend or 0) # 防御 None
            clicks = int(r.total_clicks or 0)
            orders = int(r.total_orders or 0)
            
            # 双重检查：虽然 SQL 已经过滤，但代码层再次确认更安全
            if spend > threshold and orders == 0:
                total_wasted += spend
                campaigns.append({
                    "id": str(r.id),
                    "name": r.name,
                    "spend": round(spend, 2),
                    "clicks": clicks,
                    "orders": orders
                })
            
        return {
            "total_wasted_spend": round(total_wasted, 2),
            "campaign_count": len(campaigns),
            "campaigns": campaigns
        }

    @staticmethod
    def check_high_acos(db: Session, store_id: UUID, days: int = 7, acos_threshold: float = 30.0, min_spend: float = 50.0) -> Dict[str, Any]:
        """
        检查高 ACOS：过去 N 天花费 > min_spend 且 ACOS > 阈值
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 聚合查询
        results = db.query(
            AdvertisingCampaign.id,
            AdvertisingCampaign.name,
            func.sum(CampaignPerformanceSnapshot.spend).label("total_spend"),
            func.sum(CampaignPerformanceSnapshot.sales).label("total_sales"),
            func.sum(CampaignPerformanceSnapshot.orders).label("total_orders")
        ).join(
            CampaignPerformanceSnapshot,
            AdvertisingCampaign.id == CampaignPerformanceSnapshot.campaign_id
        ).filter(
            AdvertisingCampaign.store_id == store_id,
            CampaignPerformanceSnapshot.date >= start_date,
            CampaignPerformanceSnapshot.date <= end_date,
            AdvertisingCampaign.state == 'enabled'
        ).group_by(
            AdvertisingCampaign.id
        ).having(
            (func.sum(CampaignPerformanceSnapshot.spend) > min_spend) &
            (func.sum(CampaignPerformanceSnapshot.sales) > 0) # 必须有销售额才算 ACOS
        ).all()
        
        campaigns = []
        
        for r in results:
            spend = float(r.total_spend or 0) # 防御 None
            sales = float(r.total_sales or 0)
            
            # 严格的除零保护
            if sales <= 0.001: 
                continue
            
            acos = (spend / sales) * 100
            
            if acos > acos_threshold:
                campaigns.append({
                    "id": str(r.id),
                    "name": r.name,
                    "spend": round(spend, 2),
                    "sales": round(sales, 2),
                    "acos": round(acos, 2),
                    "target_acos": acos_threshold
                })
        
        # 按 ACOS 降序排列
        campaigns.sort(key=lambda x: x['acos'], reverse=True)
            
        return {
            "campaign_count": len(campaigns),
            "campaigns": campaigns
        }

ads_diagnosis_service = AdsDiagnosisService()
