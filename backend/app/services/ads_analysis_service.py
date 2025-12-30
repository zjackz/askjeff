from datetime import date, timedelta
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.amazon_ads import (
    AmazonStore,
    InventorySnapshot, 
    AdsMetricSnapshot, 
    BusinessMetricSnapshot, 
    ProductCost
)
from app.schemas.amazon_ads import AdsMatrixPoint

class AdsAnalysisService:
    @staticmethod
    def verify_store_access(db: Session, store_id: UUID, user_id: int) -> AmazonStore:
        """验证用户是否有权限访问该店铺"""
        store = db.query(AmazonStore).filter(
            AmazonStore.id == store_id,
            AmazonStore.user_id == user_id
        ).first()
        
        if not store:
            raise HTTPException(status_code=404, detail="Store not found or access denied")
        
        return store
    
    @staticmethod
    def get_user_stores(db: Session, user_id: int) -> List[AmazonStore]:
        """获取用户的所有店铺"""
        return db.query(AmazonStore).filter(
            AmazonStore.user_id == user_id,
            AmazonStore.is_active == True
        ).all()
    
    @staticmethod
    def get_overview_data(
        db: Session,
        store_id: UUID,
        user_id: int,
        days: int = 30
    ) -> Dict:
        """
        获取全店广告概览数据
        """
        # 验证权限
        AdsAnalysisService.verify_store_access(db, store_id, user_id)
        
        # 获取矩阵数据作为基础
        matrix_data = AdsAnalysisService.get_matrix_data(db, store_id, user_id, days)
        
        if not matrix_data:
            return {
                "total_sales": 0,
                "total_spend": 0,
                "tacos": 0,
                "avg_acos": 0,
                "health_score": 0,
                "sku_count": 0,
                "quadrant_distribution": {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
            }
            
        total_sales = sum(item.total_sales for item in matrix_data)
        total_spend = sum(item.ad_spend for item in matrix_data)
        tacos = (total_spend / total_sales * 100) if total_sales > 0 else 0
        
        # 简单健康度评分逻辑 (0-100)
        # 1. TACOS 权重 40% (目标 < 15%)
        tacos_score = max(0, 100 - (tacos / 0.15 * 100)) if tacos > 0.15 else 100
        # 2. 明星产品占比权重 30%
        star_count = sum(1 for item in matrix_data if item.status == "STAR / GROWTH")
        star_ratio = star_count / len(matrix_data)
        star_score = star_ratio * 100
        # 3. 利润率权重 30%
        avg_margin = sum(item.margin for item in matrix_data) / len(matrix_data)
        margin_score = max(0, min(100, (avg_margin / 20 * 100)))
        
        health_score = (tacos_score * 0.4) + (star_score * 0.3) + (margin_score * 0.3)
        
        # 象限分布
        distribution = {
            "Q1": sum(1 for item in matrix_data if item.status == "CRITICAL / CLEARANCE"),
            "Q2": sum(1 for item in matrix_data if item.status == "STAR / GROWTH"),
            "Q3": sum(1 for item in matrix_data if item.status == "POTENTIAL / DEFENSE"),
            "Q4": sum(1 for item in matrix_data if item.status == "DROP / KILL")
        }
        
        return {
            "total_sales": round(total_sales, 2),
            "total_spend": round(total_spend, 2),
            "tacos": round(tacos, 2),
            "avg_acos": round(sum(item.acos for item in matrix_data) / len(matrix_data), 2),
            "health_score": round(health_score, 1),
            "sku_count": len(matrix_data),
            "quadrant_distribution": distribution,
            "top_movers": sorted(matrix_data, key=lambda x: x.sales, reverse=True)[:5]
        }

    @staticmethod
    def get_matrix_data(
        db: Session, 
        store_id: UUID,
        user_id: int,
        days: int = 30
    ) -> List[AdsMatrixPoint]:
        """
        获取矩阵数据
        """
        # 验证权限
        AdsAnalysisService.verify_store_access(db, store_id, user_id)
        
        today = date.today()
        start_date = today - timedelta(days=days)
        
        # 1. 获取最新库存
        latest_inv_sub = db.query(
            InventorySnapshot.sku,
            func.max(InventorySnapshot.date).label('max_date')
        ).filter(
            InventorySnapshot.store_id == store_id
        ).group_by(InventorySnapshot.sku).subquery()
        
        latest_inventory = db.query(InventorySnapshot).join(
            latest_inv_sub,
            (InventorySnapshot.sku == latest_inv_sub.c.sku) & 
            (InventorySnapshot.date == latest_inv_sub.c.max_date)
        ).filter(
            InventorySnapshot.store_id == store_id
        ).all()
        
        inv_map = {item.sku: item for item in latest_inventory}
        
        # 2. 获取产品成本 (COGS)
        costs = db.query(ProductCost).filter(ProductCost.store_id == store_id).all()
        cost_map = {item.sku: item for item in costs}
        
        # 3. 聚合销售与广告数据
        stats = db.query(
            BusinessMetricSnapshot.sku,
            BusinessMetricSnapshot.asin,
            func.sum(BusinessMetricSnapshot.total_sales_amount).label('total_sales'),
            func.sum(BusinessMetricSnapshot.total_units_ordered).label('total_units'),
            func.sum(AdsMetricSnapshot.spend).label('total_spend'),
            func.sum(AdsMetricSnapshot.sales).label('ads_sales'),
            func.sum(AdsMetricSnapshot.impressions).label('total_impressions'),
            func.sum(AdsMetricSnapshot.clicks).label('total_clicks'),
            func.sum(AdsMetricSnapshot.orders).label('total_ads_orders')
        ).outerjoin(
            AdsMetricSnapshot,
            (BusinessMetricSnapshot.store_id == AdsMetricSnapshot.store_id) &
            (BusinessMetricSnapshot.sku == AdsMetricSnapshot.sku) & 
            (BusinessMetricSnapshot.date == AdsMetricSnapshot.date)
        ).filter(
            BusinessMetricSnapshot.store_id == store_id,
            BusinessMetricSnapshot.date >= start_date
        ).group_by(
            BusinessMetricSnapshot.sku,
            BusinessMetricSnapshot.asin
        ).all()
        
        results = []
        
        for row in stats:
            sku = row.sku
            inv_item = inv_map.get(sku)
            cost_item = cost_map.get(sku)
            
            current_stock = inv_item.fba_inventory if inv_item else 0
            
            # 基础指标
            total_sales = row.total_sales or 0.0
            total_spend = row.total_spend or 0.0
            ads_sales = row.ads_sales or 0.0
            total_clicks = row.total_clicks or 0
            total_impressions = row.total_impressions or 0
            total_ads_orders = row.total_ads_orders or 0
            
            # 计算库存周转
            avg_daily_units = row.total_units / days if days > 0 else 0
            weeks_of_cover = (current_stock / (avg_daily_units * 7)) if avg_daily_units > 0 else 52.0
            weeks_of_cover = min(weeks_of_cover, 52.0)
            
            # 计算广告指标
            tacos = (total_spend / total_sales * 100) if total_sales > 0 else 0.0
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
            cvr = (total_ads_orders / total_clicks * 100) if total_clicks > 0 else 0.0
            acos = (total_spend / ads_sales * 100) if ads_sales > 0 else 0.0
            roas = (ads_sales / total_spend) if total_spend > 0 else 0.0
            
            # 计算利润率 (Margin)
            # 简化公式: (总销售额 - 总成本 - 广告费) / 总销售额
            # 总成本 = 销量 * (COGS + FBA费 + 佣金)
            unit_cost = 0.0
            if cost_item:
                referral_fee = total_sales * (cost_item.referral_fee_rate or 0.15) / (row.total_units or 1)
                unit_cost = cost_item.cogs + (cost_item.fba_fee or 0) + referral_fee
            
            total_cogs = (row.total_units or 0) * unit_cost
            net_profit = total_sales - total_cogs - total_spend
            margin = (net_profit / total_sales * 100) if total_sales > 0 else 0.0
            
            # 分类状态
            status = AdsAnalysisService._classify_sku(weeks_of_cover, tacos)
            
            results.append(AdsMatrixPoint(
                sku=sku,
                asin=row.asin,
                stock_weeks=round(weeks_of_cover, 1),
                tacos=round(tacos, 1),
                sales=total_sales,
                status=status,
                inventory_qty=current_stock,
                ad_spend=total_spend,
                total_sales=total_sales,
                ctr=round(ctr, 2),
                cvr=round(cvr, 2),
                acos=round(acos, 1),
                roas=round(roas, 2),
                margin=round(margin, 1)
            ))
            
        return results

    @staticmethod
    def _classify_sku(weeks_of_cover: float, tacos: float) -> str:
        """
        SKU 分类逻辑
        
        四象限:
        - Q1 (右上): 高库存 + 高 TACOS = CRITICAL / CLEARANCE
        - Q2 (右下): 高库存 + 低 TACOS = STAR / GROWTH
        - Q3 (左下): 低库存 + 低 TACOS = POTENTIAL / DEFENSE
        - Q4 (左上): 低库存 + 高 TACOS = DROP / KILL
        """
        if weeks_of_cover > 24:
            if tacos > 20:
                return "CRITICAL / CLEARANCE"
            else:
                return "STAR / GROWTH"
        else:
            if tacos <= 20:
                return "POTENTIAL / DEFENSE"
            else:
                return "DROP / KILL"

    @staticmethod
    def generate_diagnosis(sku: str, matrix_point: AdsMatrixPoint) -> str:
        """
        生成诊断建议 (MVP: 基于规则)
        
        未来可接入 LLM 生成更智能的建议
        """
        if matrix_point.status == "CRITICAL / CLEARANCE":
            return f"【紧急清仓】{sku} 库存积压严重且广告亏损。建议立即开启清仓模式：降低售价 15%，同时提高广告预算以加速周转，不要关注 ACOS。"
        elif matrix_point.status == "STAR / GROWTH":
            return f"【霸屏增长】{sku} 库存充足且广告表现优异。建议开启霸屏模式：提高核心关键词竞价，抢占 Top of Search，最大化销量。"
        elif matrix_point.status == "POTENTIAL / DEFENSE":
            return f"【防守控量】{sku} 表现良好但库存紧张。建议开启防守模式：适当降低预算，控制销量增速，防止断货。"
        else:
            return f"【考虑淘汰】{sku} 销量低且无库存优势。建议减少广告投入，考虑淘汰或自然出单。"

