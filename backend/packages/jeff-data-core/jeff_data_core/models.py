from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class SearchTermMetric(BaseModel):
    """
    Standardized model for Search Term performance.
    Output of the Normalization process.
    """
    date: date
    campaign_id: str
    campaign_name: str
    ad_group_id: str
    ad_group_name: str
    keyword_id: Optional[str] = None
    keyword_text: Optional[str] = None
    search_term: str
    match_type: Optional[str] = None
    
    # Metrics
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    sales: float = 0.0
    orders: int = 0
    units: int = 0
    
    # Computed
    acos: Optional[float] = None
    cpc: Optional[float] = None
    ctr: Optional[float] = None

    def compute_derived_metrics(self):
        if self.sales > 0:
            self.acos = (self.spend / self.sales) * 100
        if self.clicks > 0:
            self.cpc = self.spend / self.clicks
            self.ctr = (self.clicks / self.impressions) * 100
