"""
Amazon Selling Partner API Connector

用于从 Amazon SP-API 获取数据
"""

import time
from typing import Any, Dict, Generator, Optional
from datetime import date, datetime
import httpx

from ..connectors.base import BaseConnector, ConnectorConfig
from ..normalizers.base import BaseNormalizer
from ..models import StandardProduct, StandardInventory, StandardOrder


class AmazonSPConfig(ConnectorConfig):
    """Amazon SP-API 配置"""
    client_id: str
    client_secret: str
    refresh_token: str
    marketplace_id: str  # ATVPDKIKX0DER, A1PA6795UKMFR9
    region: str = "NA"  # NA, EU, FE

    @property
    def base_url(self) -> str:
        if self.region == "EU":
            return "https://sellingpartnerapi-eu.amazon.com"
        elif self.region == "FE":
            return "https://sellingpartnerapi-fe.amazon.com"
        return "https://sellingpartnerapi-na.amazon.com"

    @property
    def token_url(self) -> str:
        return "https://api.amazon.com/auth/o2/token"


class AmazonSPConnector(BaseConnector):
    """Amazon Selling Partner API 连接器

    支持：
    - 库存报告（FBA Inventory）
    - 业务报告（Business Reports）
    - 订单数据（Orders）
    """

    def __init__(self, config: AmazonSPConfig):
        super().__init__(config)
        self.config: AmazonSPConfig = config
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self.client = httpx.Client(timeout=self.config.timeout)

    @property
    def source_type(self) -> str:
        return "amazon_sp"

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        if not self._access_token or time.time() > self._token_expires_at:
            self._refresh_access_token()

        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

    def _refresh_access_token(self):
        """刷新访问令牌"""
        response = self.client.post(
            self.config.token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.config.refresh_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
        )
        response.raise_for_status()
        data = response.json()

        self._access_token = data.get("access_token")
        self._token_expires_at = time.time() + data.get("expires_in", 3600) - 60

    def validate_credentials(self) -> bool:
        """验证凭证"""
        try:
            self._refresh_access_token()
            return True
        except Exception as e:
            return False

    def fetch_data(
        self,
        start_date: date,
        end_date: date,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """获取数据

        支持的接口：
        - inventory: 库存报告
        - business: 业务报告
        - orders: 订单数据
        """
        report_type = kwargs.get("report_type", "inventory")

        if report_type == "inventory":
            yield from self._fetch_inventory_report(start_date, end_date)
        elif report_type == "business":
            yield from self._fetch_business_report(start_date, end_date)
        elif report_type == "orders":
            yield from self._fetch_orders(start_date, end_date)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

    def _fetch_inventory_report(
        self,
        start_date: date,
        end_date: date
    ) -> Generator[Dict[str, Any], None, None]:
        """获取库存报告

        Amazon SP-API 文档：
        https://developer-docs.amazon.com/sp-api/docs/reports-api/reports-v2
        """
        url = f"{self.base_url}/reports/2024-06-01/reports/inventory"

        try:
            # 创建报告请求
            response = self.client.post(
                url,
                headers=self._get_headers(),
                json={
                    "reportType": "INVENTORY_EVENT_DATA",
                    "dataStartTime": start_date.isoformat(),
                    "dataEndTime": end_date.isoformat(),
                    "marketplaceIds": [self.config.marketplace_id],
                    "version": "V2"
                }
            )
            response.raise_for_status()

            report_id = response.json().get("reportId")

            # 轮询报告状态
            download_url = self._wait_for_report(url, report_id)

            # 下载和解析报告
            yield from self._download_and_parse_inventory(download_url)

        except Exception as e:
            yield {
                "error": str(e),
                "report_type": "inventory",
                "date": start_date.isoformat()
            }

    def _fetch_business_report(
        self,
        start_date: date,
        end_date: date
    ) -> Generator[Dict[str, Any], None, None]:
        """获取业务报告"""
        url = f"{self.base_url}/reports/2024-06-01/reports/salesAndTrafficBusiness"

        try:
            response = self.client.post(
                url,
                headers=self._get_headers(),
                json={
                    "reportType": "SALES_AND_TRAFFIC_BUSINESS_DATA",
                    "dataStartTime": start_date.isoformat(),
                    "dataEndTime": end_date.isoformat(),
                    "marketplaceIds": [self.config.marketplace_id],
                    "version": "V2"
                }
            )
            response.raise_for_status()

            report_id = response.json().get("reportId")

            download_url = self._wait_for_report(url, report_id)

            yield from self._download_and_parse_business(download_url)

        except Exception as e:
            yield {
                "error": str(e),
                "report_type": "business",
                "date": start_date.isoformat()
            }

    def _fetch_orders(
        self,
        start_date: date,
        end_date: date
    ) -> Generator[Dict[str, Any], None, None]:
        """获取订单数据"""
        url = f"{self.base_url}/orders/v0/orders"

        try:
            response = self.client.get(
                url,
                headers=self._get_headers(),
                params={
                    "MarketplaceId": self.config.marketplace_id,
                    "CreatedAfter": start_date.isoformat(),
                    "CreatedBefore": end_date.isoformat(),
                    "MaxResultsPerPage": 100
                }
            )
            response.raise_for_status()

            orders = response.json().get("Payload", {}).get("Orders", [])

            for order in orders:
                yield self._normalize_order(order)

        except Exception as e:
            yield {
                "error": str(e),
                "report_type": "orders",
                "date": start_date.isoformat()
            }

    def _wait_for_report(self, base_url: str, report_id: str, max_retries: int = 30) -> Optional[str]:
        """轮询报告状态"""
        url = f"{base_url}/{report_id}"

        for attempt in range(max_retries):
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()

            status = response.json().get("processingStatus")

            if status == "DONE":
                return response.json().get("reportDocumentId")
            elif status == "CANCELLED":
                return None
            elif status == "FATAL":
                return None

            time.sleep(2 * (attempt + 1))

        return None

    def _download_and_parse_inventory(
        self,
        download_url: str
    ) -> Generator[Dict[str, Any], None, None]:
        """下载和解析库存报告"""
        response = self.client.get(download_url)

        # 简化：返回 JSON 响应
        yield response.json()

    def _download_and_parse_business(
        self,
        download_url: str
    ) -> Generator[Dict[str, Any], None, None]:
        """下载和解析业务报告"""
        response = self.client.get(download_url)

        # 简化：返回 JSON 响应
        yield response.json()

    def _normalize_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """标准化订单数据"""
        return {
            "asin": order.get("ASIN"),
            "order_id": order.get("AmazonOrderId"),
            "order_status": order.get("OrderStatus"),
            "purchase_date": order.get("PurchaseDate"),
            "order_total": order.get("OrderTotal", {}).get("Amount"),
            "currency": order.get("OrderTotal", {}).get("CurrencyCode", "USD"),
            "items_count": len(order.get("OrderItems", []))
        }
