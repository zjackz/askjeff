from datetime import date, datetime
from typing import List, Optional, Dict
from pydantic import BaseModel
from uuid import UUID

class AmazonStoreSchema(BaseModel):
    """店铺信息 Schema"""
    id: UUID
    store_name: str
    marketplace_id: str
    marketplace_name: str
    seller_id: str
    is_active: bool
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdsMatrixPoint(BaseModel):
    """矩阵数据点"""
    sku: str
    asin: str
    stock_weeks: float
    tacos: float
    sales: float
    status: str
    inventory_qty: int
    ad_spend: float
    total_sales: float
    
    # 新增核心指标
    ctr: float  # 点击率
    cvr: float  # 转化率
    acos: float # 广告成本占比
    roas: float # 广告支出回报率
    margin: float # 广告后净利润率

class AdsMetricTrend(BaseModel):
    """指标趋势"""
    date: str
    value: float

class AdsDiagnosis(BaseModel):
    """SKU 诊断结果"""
    sku: str
    asin: str
    status: str
    diagnosis: str
    metrics: Dict[str, float]

class AdsAnalysisResponse(BaseModel):
    """分析响应"""
    matrix_data: List[AdsMatrixPoint]
    total_skus: int
