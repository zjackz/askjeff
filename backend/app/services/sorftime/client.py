import httpx
import json
import logging
from typing import Dict, Any, Optional
from functools import wraps
import asyncio
from .models import SorftimeResponse

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """请求失败自动重试（指数退避）"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception: Exception | None = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPError, httpx.TimeoutException) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            "请求失败（第 %s/%s 次），%s 秒后重试：%s",
                            attempt + 1,
                            max_retries,
                            wait_time,
                            str(e),
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("请求失败：已达到最大重试次数（%s）：%s", max_retries, str(e))
            if last_exception is None:
                raise RuntimeError("重试装饰器状态异常：未捕获到异常但未返回结果")
            raise last_exception
        return wrapper
    return decorator


class SorftimeClient:
    """
    Comprehensive client for Sorftime Amazon API.
    
    Supports all 45 API endpoints with:
    - Automatic retry on failure
    - Request/response logging
    - Error handling
    - Type validation
    """
    
    BASE_URL = "https://standardapi.sorftime.com/api"
    
    def __init__(self, account_sk: str, db: Optional[Any] = None):
        """
        Initialize Sorftime client.
        
        Args:
            account_sk: Sorftime API key
            db: Database session for logging (optional)
        """
        self.account_sk = account_sk
        self.db = db
        self.headers = {
            "Authorization": f"BasicAuth {self.account_sk}",
            "Content-Type": "application/json;charset=UTF-8"
        }
        self._request_count = 0

    @retry_on_failure(max_retries=3, delay=1.0)
    async def _post(
        self, 
        endpoint: str, 
        domain: int, 
        payload: Any,
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Make a POST request to Sorftime API.
        """
        from app.services.log_service import LogService  # Lazy import to avoid circular dependency
        import time

        url = f"{self.BASE_URL}/{endpoint}"
        params = {"domain": domain}
        
        # Convert Pydantic models to dict if needed
        json_payload = payload
        if hasattr(payload, "model_dump"):
            json_payload = payload.model_dump(exclude_none=True)
        elif isinstance(payload, list):
            json_payload = [
                item.model_dump(exclude_none=True) if hasattr(item, "model_dump") else item 
                for item in payload
            ]

        self._request_count += 1
        start_time = time.perf_counter()
        
        # trust_env=False ignores system proxy settings which may be broken
        async with httpx.AsyncClient(verify=False, trust_env=False, timeout=timeout) as client:
            try:
                response = await client.post(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    json=json_payload
                )
                duration = round((time.perf_counter() - start_time) * 1000, 2)
                
                response_data = {}
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {"raw": response.text[:500]}

                # Log to DB if session is available
                if self.db:
                    try:
                        # 提取 Quota 信息
                        quota_info = {
                            "requestLeft": response_data.get("requestLeft"),
                            "requestConsumed": response_data.get("requestConsumed"),
                            "requestCount": response_data.get("requestCount"),
                            "code": response_data.get("code"),
                            "message": response_data.get("message")
                        }
                        
                        # 判断是否成功
                        is_success = response.status_code < 400 and response_data.get("code") == 0
                        
                        # 构建 context
                        context = {
                            "platform": "Sorftime",
                            "url": str(response.url),
                            "method": "POST",
                            "request": json_payload,
                            "response": quota_info,
                            "status_code": response.status_code,
                            "duration_ms": duration,
                            "domain": domain
                        }
                        
                        # 如果失败，记录原始响应以便调试
                        if not is_success:
                            context["raw_response"] = response.text[:2000]  # 截断到 2000 字符
                            context["error_detail"] = {
                                "http_status": response.status_code,
                                "api_code": response_data.get("code"),
                                "api_message": response_data.get("message")
                            }
                        
                        LogService.log(
                            self.db,
                            level="info" if is_success else "error",
                            category="external_api",
                            message=f"Sorftime API {endpoint}",
                            context=context,
                            status="info"
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log to DB: {log_err}")

                return response_data
                
            except Exception as e:
                # Log error if DB available
                if self.db:
                    LogService.log(
                        self.db,
                        level="error",
                        category="external_api",
                        message=f"Sorftime API {endpoint} Failed",
                        context={
                            "platform": "Sorftime",
                            "url": url,
                            "method": "POST",
                            "error": str(e)
                        },
                        status="new"
                    )
                raise

    # ==================== Basic Query APIs (1-9) ====================
    
    async def product_request(
        self, 
        asin: str, 
        trend: int = 1,
        domain: int = 1,
        query_trend_start: Optional[str] = None,
        query_trend_end: Optional[str] = None
    ) -> SorftimeResponse:
        """1. ProductRequest - Fetch product details"""
        payload = {
            "ASIN": asin,
            "Trend": trend,
            "QueryTrendStartDt": query_trend_start,
            "QueryTrendEndDt": query_trend_end,
            "gzip": 0
        }
        data = await self._post("ProductRequest", domain, payload)
        return SorftimeResponse(**data)

    async def category_request(
        self,
        node_id: str,
        domain: int = 1,
        query_start: Optional[str] = None,
        query_date: Optional[str] = None
    ) -> SorftimeResponse:
        """2. CategoryRequest - Fetch category best sellers"""
        payload = {
            "nodeId": node_id,
            "queryStart": query_start,
            "queryDate": query_date
        }
        data = await self._post("CategoryRequest", domain, payload)
        return SorftimeResponse(**data)

    async def category_tree(self, domain: int = 1, gzip: int = 0) -> SorftimeResponse:
        """3. CategoryTree - Fetch full category tree"""
        payload = {"gzip": gzip}
        data = await self._post("CategoryTree", domain, payload, timeout=120.0)
        return SorftimeResponse(**data)

    async def category_trend(
        self,
        node_id: str,
        trend_index: int,
        domain: int = 1
    ) -> SorftimeResponse:
        """4. CategoryTrend - Fetch category trend data"""
        payload = {"nodeId": node_id, "trendIndex": trend_index}
        data = await self._post("CategoryTrend", domain, payload)
        return SorftimeResponse(**data)

    async def category_products(
        self,
        node_id: str,
        page: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """5. CategoryProducts - Fetch products in category"""
        payload = {"nodeId": node_id, "page": page}
        data = await self._post("CategoryProducts", domain, payload)
        return SorftimeResponse(**data)

    async def product_query(
        self,
        query_type: int,
        pattern: Any,
        page: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """6. ProductQuery - Search products"""
        payload = {
            "query": 1,
            "queryType": query_type,
            "pattern": pattern,
            "page": page
        }
        data = await self._post("ProductQuery", domain, payload)
        return SorftimeResponse(**data)

    async def keyword_query(
        self,
        pattern: Dict[str, Any],
        page_index: int = 1,
        page_size: int = 20,
        domain: int = 1
    ) -> SorftimeResponse:
        """7. KeywordQuery - Search keywords"""
        payload = {
            "pattern": pattern,
            "pageIndex": page_index,
            "pageSize": page_size
        }
        data = await self._post("KeywordQuery", domain, payload)
        return SorftimeResponse(**data)

    async def keyword_request(
        self,
        keyword: str,
        domain: int = 1
    ) -> SorftimeResponse:
        """8. KeywordRequest - Fetch keyword details"""
        payload = {"keyword": keyword}
        data = await self._post("KeywordRequest", domain, payload)
        return SorftimeResponse(**data)

    async def keyword_search_results(
        self,
        keyword: str,
        page: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """9. KeywordSearchResults - Fetch keyword search results"""
        payload = {"keyword": keyword, "page": page}
        data = await self._post("KeywordSearchResults", domain, payload)
        return SorftimeResponse(**data)

    # ==================== Advanced Data APIs (10-12) ====================

    async def asin_sales_volume(
        self,
        asin: str,
        query_start: Optional[str] = None,
        query_end: Optional[str] = None,
        page: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """10. AsinSalesVolume - Fetch ASIN sales volume"""
        payload = {
            "asin": asin,
            "queryDate": query_start,
            "queryEndDate": query_end,
            "page": page
        }
        data = await self._post("AsinSalesVolume", domain, payload)
        return SorftimeResponse(**data)

    async def product_variation_history(
        self,
        asin: str,
        domain: int = 1
    ) -> SorftimeResponse:
        """11. ProductVariationHistory - Fetch variation history"""
        payload = {"asin": asin}
        data = await self._post("ProductVariationHistory", domain, payload)
        return SorftimeResponse(**data)

    async def product_trend(
        self,
        asin: str,
        date_range: str,
        trend_type: int,
        domain: int = 1
    ) -> SorftimeResponse:
        """12. ProductTrend - Fetch product trend (Not yet developed)"""
        payload = {
            "asin": asin,
            "dateRange": date_range,
            "trendType": trend_type
        }
        data = await self._post("ProductTrend", domain, payload)
        return SorftimeResponse(**data)

    # ==================== Real-time Collection APIs (13-20) ====================

    async def product_realtime_request(
        self,
        asin: str,
        update: int = 24,
        domain: int = 1
    ) -> SorftimeResponse:
        """13. ProductRealtimeRequest - Request real-time product data"""
        payload = {"asin": asin, "update": update}
        data = await self._post("ProductRealtimeRequest", domain, payload)
        return SorftimeResponse(**data)

    async def product_realtime_status_query(
        self,
        query_date: str,
        domain: int = 1
    ) -> SorftimeResponse:
        """14. ProductRealtimeRequestStatusQuery - Query real-time request status"""
        payload = {"queryDate": query_date}
        data = await self._post("ProductRealtimeRequestStatusQuery", domain, payload)
        return SorftimeResponse(**data)

    async def product_reviews_collection(
        self,
        asin: str,
        mode: int = 0,
        star: Optional[str] = None,
        only_purchase: int = 0,
        page: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """15. ProductReviewsCollection - Collect product reviews"""
        payload = {
            "asin": asin,
            "mode": mode,
            "star": star,
            "onlyPurchase": only_purchase,
            "page": page
        }
        data = await self._post("ProductReviewsCollection", domain, payload)
        return SorftimeResponse(**data)

    async def product_reviews_collection_status_query(
        self,
        asin: str,
        update: int = 24,
        domain: int = 1
    ) -> SorftimeResponse:
        """16. ProductReviewsCollectionStatusQuery - Query review collection status"""
        payload = {"asin": asin, "Update": update}
        data = await self._post("ProductReviewsCollectionStatusQuery", domain, payload)
        return SorftimeResponse(**data)

    async def product_reviews_query(
        self,
        asin: str,
        query_start: str,
        star: Optional[str] = None,
        only_purchase: int = 0,
        page: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """17. ProductReviewsQuery - Query collected reviews"""
        payload = {
            "asin": asin,
            "queryStart": query_start,
            "star": star,
            "onlyPurchase": only_purchase,
            "page": page
        }
        data = await self._post("ProductReviewsQuery", domain, payload)
        return SorftimeResponse(**data)

    async def similar_product_realtime_request(
        self,
        image: str,
        domain: int = 1
    ) -> SorftimeResponse:
        """18. SimilarProductRealtimeRequest - Request similar products by image"""
        payload = {"image": image}
        data = await self._post("SimilarProductRealtimeRequest", domain, payload)
        return SorftimeResponse(**data)

    async def similar_product_realtime_request_status_query(
        self,
        update: int = 24,
        domain: int = 1
    ) -> SorftimeResponse:
        """19. SimilarProductRealtimeRequestStatusQuery - Query similar product request status"""
        payload = {"Update": update}
        data = await self._post("SimilarProductRealtimeRequestStatusQuery", domain, payload)
        return SorftimeResponse(**data)

    async def similar_product_realtime_request_collection(
        self,
        task_id: str,
        domain: int = 1
    ) -> SorftimeResponse:
        """20. SimilarProductRealtimeRequestCollection - Collect similar product results"""
        payload = {"taskId": task_id}
        data = await self._post("SimilarProductRealtimeRequestCollection", domain, payload)
        return SorftimeResponse(**data)

    # ==================== Keyword Extended APIs (21-25) ====================

    async def keyword_search_result_trend(
        self,
        keyword: str,
        page_index: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """21. KeywordSearchResultTrend - Fetch keyword search result trend"""
        payload = {"keyword": keyword, "pageIndex": page_index}
        data = await self._post("KeywordSearchResultTrend", domain, payload)
        return SorftimeResponse(**data)

    async def category_request_keyword(
        self,
        node_id: str,
        page_index: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """22. CategoryRequestKeyword - Reverse lookup keywords by category"""
        payload = {"nodeId": node_id, "pageIndex": page_index}
        data = await self._post("CategoryRequestKeyword", domain, payload)
        return SorftimeResponse(**data)

    async def asin_request_keyword(
        self,
        asin: str,
        page_index: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """23. ASINRequestKeyword - Reverse lookup keywords by ASIN"""
        payload = {"asin": asin, "pageIndex": page_index}
        data = await self._post("ASINRequestKeyword", domain, payload)
        return SorftimeResponse(**data)

    async def keyword_product_ranking(
        self,
        keyword: str,
        page_index: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """24. KeywordProductRanking - Fetch product ranking for keyword"""
        payload = {"keyword": keyword, "pageIndex": page_index}
        data = await self._post("KeywordProductRanking", domain, payload)
        return SorftimeResponse(**data)

    async def asin_keyword_ranking(
        self,
        keyword: str,
        asin: str,
        query_start: Optional[str] = None,
        query_end: Optional[str] = None,
        page: int = 1,
        domain: int = 1
    ) -> SorftimeResponse:
        """25. ASINKeywordRanking - Fetch ASIN ranking trend for keyword"""
        payload = {
            "keyword": keyword,
            "asin": asin,
            "queryStart": query_start,
            "queryEnd": query_end,
            "page": page
        }
        data = await self._post("ASINKeywordRanking", domain, payload)
        return SorftimeResponse(**data)

    # ==================== Monitoring APIs (26-42) ====================
    # Note: These are subscription/monitoring APIs that consume points instead of requests

    async def generic_monitoring_api(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        domain: int = 1
    ) -> SorftimeResponse:
        """
        Generic method for monitoring APIs (26-42).
        These APIs have complex payloads and are used for task management.
        """
        data = await self._post(endpoint, domain, payload)
        return SorftimeResponse(**data)

    # ==================== Account/Billing APIs (43-45) ====================

    async def coin_query(self, domain: int = 1) -> SorftimeResponse:
        """43. CoinQuery - Query remaining points"""
        payload = {}
        data = await self._post("CoinQuery", domain, payload)
        return SorftimeResponse(**data)

    async def coin_stream(
        self,
        platform: int = 0,
        query_date: Optional[list] = None,
        page_index: int = 1,
        page_size: int = 20,
        domain: int = 1
    ) -> SorftimeResponse:
        """44. CoinStream - Query point usage details"""
        payload = {
            "Platform": platform,
            "QueryDate": query_date or [],
            "PageIndex": page_index,
            "PageSize": page_size
        }
        data = await self._post("CoinStream", domain, payload)
        return SorftimeResponse(**data)

    async def request_stream(
        self,
        platform: int = 0,
        domain: int = 1
    ) -> SorftimeResponse:
        """45. RequestStream - Query request usage details"""
        payload = {"Platform": platform}
        data = await self._post("RequestStream", domain, payload)
        return SorftimeResponse(**data)

    # ==================== Utility Methods ====================

    def get_request_count(self) -> int:
        """Get total number of requests made by this client instance"""
        return self._request_count

    def reset_request_count(self):
        """Reset request counter"""
        self._request_count = 0
