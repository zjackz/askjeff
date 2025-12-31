from datetime import datetime, date
from typing import Any, Dict, Type
from pydantic import BaseModel

from jeff_data_core.normalizers.base import BaseNormalizer
from jeff_data_core.models import SearchTermMetric

class AmazonSearchTermNormalizer(BaseNormalizer):
    """
    Normalizes Amazon Sponsored Products Search Term Report data.
    """

    def normalize(self, raw_record: Dict[str, Any]) -> SearchTermMetric:
        # Amazon report date format is usually YYYY-MM-DD, but sometimes it's not in the row
        # If the row doesn't have a date, we might need to pass it from metadata.
        # For now, let's assume the raw_record has been enriched with 'reportDate' or similar 
        # during the extraction phase, or the report itself contains a date column.
        
        # NOTE: SP Search Term report usually has 'startDate' and 'endDate' in the summary, 
        # but row-level data might not have a date if it's a summary report.
        # We assume the raw_record includes a 'date' field injected by the connector or present in the row.
        
        record_date = raw_record.get("date")
        if isinstance(record_date, str):
            record_date = datetime.strptime(record_date, "%Y-%m-%d").date()
        elif not record_date:
            # Fallback to today if missing (should be handled better in production)
            record_date = date.today()

        metric = SearchTermMetric(
            date=record_date,
            campaign_id=str(raw_record.get("campaignId")),
            campaign_name=raw_record.get("campaignName", "Unknown"),
            ad_group_id=str(raw_record.get("adGroupId")),
            ad_group_name=raw_record.get("adGroupName", "Unknown"),
            keyword_id=str(raw_record.get("keywordId")),
            keyword_text=raw_record.get("keywordText"),
            search_term=raw_record.get("query", ""), # 'query' is the search term in SP reports
            match_type=raw_record.get("matchType"),
            
            # Metrics Mapping
            impressions=int(raw_record.get("impressions", 0)),
            clicks=int(raw_record.get("clicks", 0)),
            spend=float(raw_record.get("cost", 0.0)), # Amazon uses 'cost'
            sales=float(raw_record.get("sales14d", 0.0)), # Attribution window 14d
            orders=int(raw_record.get("orders14d", 0)),
            units=int(raw_record.get("unitsSold14d", 0))
        )
        
        metric.compute_derived_metrics()
        return metric

    @property
    def target_model(self) -> Type[BaseModel]:
        return SearchTermMetric
