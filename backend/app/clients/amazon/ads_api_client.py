from typing import Any, Dict, List
from app.clients.amazon.base_client import AmazonBaseClient

class AdsApiClient(AmazonBaseClient):
    """
    Amazon Advertising API client
    封装广告报告、Campaign 管理接口
    """
    def __init__(self, region: str = "na", refresh_token: str = None, profile_id: str = None):
        super().__init__(refresh_token)
        # Ads API Endpoints
        self.host = "https://advertising-api.amazon.com"
        if region == "eu":
            self.host = "https://advertising-api-eu.amazon.com"
            
        self.profile_id = profile_id  # Header 需要 Amazon-Advertising-API-Scope
        
    def _make_ads_request(self, method: str, path: str, **kwargs) -> Any:
        # 重写请求方法，添加 Ads 特有 Header
        headers = kwargs.get("headers", {})
        if self.profile_id:
            headers["Amazon-Advertising-API-Scope"] = self.profile_id
        headers["Amazon-Advertising-API-ClientId"] = self.client_id
        
        kwargs["headers"] = headers
        url = f"{self.host}{path}"
        return self._make_request(method, url, **kwargs)

    def list_campaigns(self, state_filter: str = "enabled") -> List[Dict]:
        """
        获取广告活动列表 (Sponsored Products)
        """
        # API v3
        path = "/sp/campaigns/list"
        body = {
            "stateFilter": {"include": [state_filter]}
        }
        # 这里的 Content-Type 特殊
        headers = {
            "Content-Type": "application/vnd.spCampaign.v3+json",
            "Accept": "application/vnd.spCampaign.v3+json"
        }
        response = self._make_ads_request("POST", path, json=body, headers=headers)
        return response.get("campaigns", [])

    def request_report(
        self, 
        report_date: str, 
        metrics: List[str],
        report_type: str = "spCampaigns"
    ) -> str:
        """
        请求广告报告 (异步)
        返回 reportId
        """
        path = "/reporting/reports"
        body = {
            "name": f"SP Report {report_date}",
            "startDate": report_date,
            "endDate": report_date,
            "configuration": {
                "adProduct": "SPONTANEOUS_PRODUCTS", # 注意: 实际值需查阅文档，此处为示例
                "groupBy": ["campaign"],
                "columns": metrics,
                "reportTypeId": report_type,
                "format": "GZIP_JSON",
                "timeUnit": "DAILY"
            }
        }
        response = self._make_ads_request("POST", path, json=body)
        return response["reportId"]
    
    def get_report_status(self, report_id: str) -> Dict[str, Any]:
        path = f"/reporting/reports/{report_id}"
        return self._make_ads_request("GET", path)
