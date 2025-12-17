import httpx
import json
import logging
from typing import Dict, Any, Optional
from functools import wraps
import asyncio
from .models import SorftimeResponse

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry failed requests"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPError, httpx.TimeoutException) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {str(e)}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Request failed after {max_retries} attempts: {str(e)}")
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
    
    def __init__(self, account_sk: str):
        """
        Initialize Sorftime client.
        
        Args:
            account_sk: Sorftime API key
        """
        self.account_sk = account_sk
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
        
        Args:
            endpoint: API endpoint name (e.g., 'ProductRequest')
            domain: Domain code (1: US, 2: GB, etc.)
            payload: Request payload
            timeout: Request timeout in seconds
            
        Returns:
            API response as dictionary
            
        Raises:
            httpx.HTTPError: On network errors
            httpx.TimeoutException: On timeout
        """
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
        logger.info(
            f"Sorftime API Request #{self._request_count}: {endpoint} | "
            f"Domain: {domain} | Payload: {json.dumps(json_payload)[:200]}..."
        )
        
        # trust_env=False ignores system proxy settings which may be broken
        async with httpx.AsyncClient(verify=False, trust_env=False, timeout=timeout) as client:
            response = await client.post(
                url, 
                headers=self.headers, 
                params=params, 
                json=json_payload
            )
            
            # Sorftime uses custom HTTP status codes (e.g., 694 for quota exceeded)
            # Don't raise on non-2xx, return the response body instead
            try:
                data = response.json()
                logger.info(
                    f"Sorftime API Response #{self._request_count}: "
                    f"Code={data.get('code', 'N/A')}, "
                    f"Message={data.get('message', 'N/A')[:100]}"
                )
                return data
            except json.JSONDecodeError:
                logger.error(
                    f"Failed to decode JSON response. "
                    f"Status: {response.status_code}, Text: {response.text[:500]}"
                )
                # Return error response for frontend display
                return {
                    "code": response.status_code,
                    "message": f"Non-JSON response: {response.text[:200]}",
                    "data": None
                }

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
