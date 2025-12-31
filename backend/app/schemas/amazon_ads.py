from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel

# --- Existing Schemas (Restored) ---

class AmazonStoreSchema(BaseModel):
    id: UUID
    store_name: str
    marketplace_name: str
    currency_code: str
    
    class Config:
        from_attributes = True

class AdsMatrixPoint(BaseModel):
    sku: str
    asin: str
    status: str  # 'healthy', 'risk', 'opportunity'
    stock_weeks: float
    tacos: float
    sales: float
    ad_spend: float
    ctr: float
    cvr: float
    acos: float
    roas: float
    margin: float

class AdsDiagnosis(BaseModel):
    sku: str
    asin: str
    status: str
    diagnosis: str
    metrics: Dict[str, Any]

# --- New Campaign Schemas ---

class CampaignBase(BaseModel):
    name: str
    state: str
    campaign_type: str
    targeting_type: str
    daily_budget: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class CampaignMetrics(BaseModel):
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    sales: float = 0.0
    orders: int = 0
    units: int = 0
    
    # Derived metrics
    ctr: float = 0.0
    cpc: float = 0.0
    acos: float = 0.0
    roas: float = 0.0
    cvr: float = 0.0

class CampaignDetail(CampaignBase, CampaignMetrics):
    id: UUID
    campaign_id: str # Amazon ID

    class Config:
        from_attributes = True

class CampaignListResponse(BaseModel):
    total: int
    items: List[CampaignDetail]
    page: int
    limit: int

# --- Diagnosis Schemas ---

class WastedSpendCampaign(BaseModel):
    id: str
    name: str
    spend: float
    clicks: int
    orders: int

class WastedSpendResponse(BaseModel):
    total_wasted_spend: float
    campaign_count: int
    campaigns: List[WastedSpendCampaign]

class HighAcosCampaign(BaseModel):
    id: str
    name: str
    spend: float
    sales: float
    acos: float
    target_acos: float

class HighAcosResponse(BaseModel):
    campaign_count: int
    campaigns: List[HighAcosCampaign]
