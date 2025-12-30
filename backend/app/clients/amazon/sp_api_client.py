from typing import Any, Dict, Optional
from app.clients.amazon.base_client import AmazonBaseClient
from app.config import settings

class SpApiClient(AmazonBaseClient):
    """
    Amazon Selling Partner API (SP-API) 客户端
    封装库存、业务报告等接口
    """
    def __init__(self, region: str = "us-east-1", refresh_token: str = None):
        super().__init__(refresh_token)
        # SP-API Endpoints
        self.host = "https://sellingpartnerapi-na.amazon.com"
        if region == "eu-west-1":
            self.host = "https://sellingpartnerapi-eu.amazon.com"
        
    def get_inventory_summary(
        self, 
        marketplace_id: str,
        details: bool = True
    ) -> Dict[str, Any]:
        """
        获取 FBA 库存数据 (通过 Reports API 简化模拟)
        注意：实际通常使用 GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA 报告
        这里展示直接调用 API 的示例 (如果有对应 API)，或者封装 Report 生命周期
        """
        # 示例：调用 FBA Inventory API (v1)
        url = f"{self.host}/fba/inventory/v1/summaries"
        params = {
            "details": str(details).lower(),
            "marketplaceIds": marketplace_id,
            "granularityType": "Marketplace",
            "granularityId": marketplace_id
        }
        
        return self._make_request("GET", url, params=params)

    def create_report(
        self, 
        report_type: str, 
        marketplace_ids: list[str],
        data_start_time: str = None,
        data_end_time: str = None
    ) -> str:
        """
        创建一般 SP-API 报告 (如 GET_SALES_AND_TRAFFIC_REPORT)
        返回 reportId
        """
        url = f"{self.host}/reports/2021-06-30/reports"
        body = {
            "reportType": report_type,
            "marketplaceIds": marketplace_ids,
        }
        if data_start_time:
            body["dataStartTime"] = data_start_time
        if data_end_time:
            body["dataEndTime"] = data_end_time
            
        response = self._make_request("POST", url, json=body)
        return response["reportId"]

    def get_report_document(self, report_document_id: str) -> Dict[str, Any]:
        """
        获取报告下载链接
        """
        url = f"{self.host}/reports/2021-06-30/documents/{report_document_id}"
        return self._make_request("GET", url)

    def get_product_fees_estimate(
        self, 
        marketplace_id: str,
        asin: str,
        price: float,
        currency_code: str = "USD"
    ) -> Dict[str, Any]:
        """
        获取产品费用预估 (FBA Fee, Referral Fee)
        """
        url = f"{self.host}/products/fees/v0/items/{asin}/feesEstimate"
        body = {
            "FeesEstimateRequest": {
                "MarketplaceId": marketplace_id,
                "PriceToEstimateFees": {
                    "ListingPrice": {
                        "CurrencyCode": currency_code,
                        "Amount": price
                    }
                },
                "Identifier": asin,
                "IsAmazonFulfilled": True 
            }
        }
        return self._make_request("POST", url, json=body)
