import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from .models import SorftimeResponse

logger = logging.getLogger(__name__)

class SorftimeClient:
    BASE_URL = "https://standardapi.sorftime.com/api"
    
    def __init__(self, account_sk: str = "uis1m3dyr0exaecvmmnnwlfzdvdkqt09"):
        self.account_sk = account_sk
        self.headers = {
            "Authorization": f"BasicAuth {self.account_sk}",
            "Content-Type": "application/json;charset=UTF-8"
        }

    async def _post(self, endpoint: str, domain: int, payload: Any) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"domain": domain}
        
        # Convert Pydantic models to dict if needed
        json_payload = payload
        if hasattr(payload, "model_dump"):
            json_payload = payload.model_dump(exclude_none=True)
        elif isinstance(payload, list):
            json_payload = [item.model_dump(exclude_none=True) if hasattr(item, "model_dump") else item for item in payload]

        logger.info(f"Sorftime API Request: {url} | Domain: {domain} | Payload: {json_payload}")
        
        # trust_env=False ignores system proxy settings (HTTP_PROXY, etc.) which are currently broken
        async with httpx.AsyncClient(verify=False, trust_env=False) as client:
            try:
                response = await client.post(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    json=json_payload, 
                    timeout=60.0
                )
                # Sorftime uses custom HTTP status codes (e.g., 694 for quota exceeded)
                # We should not raise an exception here, but return the response body
                try:
                    return response.json()
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON. Status: {response.status_code}, Text: {response.text}")
                    # Return a mock error response so the frontend can display something
                    return {
                        "code": response.status_code,
                        "message": f"Non-JSON response: {response.text}",
                        "data": None
                    }
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Request Failed: {str(e)}")
                raise

    async def fetch_product_details(self, asins: List[str], domain: int = 1) -> SorftimeResponse:
        """Fetch details for a list of ASINs."""
        # Join ASINs with comma as per API doc
        asin_str = ",".join(asins)
        # Payload keys must be PascalCase as per doc: ASIN, Trend
        payload = {"ASIN": asin_str, "Trend": 1}
        data = await self._post("ProductRequest", domain, payload)
        return SorftimeResponse(**data)

    async def fetch_category_best_sellers(self, node_id: str, domain: int = 1) -> SorftimeResponse:
        """Fetch Best Sellers for a category node."""
        payload = {"nodeId": node_id}
        data = await self._post("CategoryRequest", domain, payload)
        return SorftimeResponse(**data)

    async def fetch_category_tree(self, domain: int = 1) -> SorftimeResponse:
        """Fetch the full category tree."""
        payload = {"gzip": 0}
        data = await self._post("CategoryTree", domain, payload)
        return SorftimeResponse(**data)

    async def fetch_category_trend(self, node_id: str, trend_index: int, domain: int = 1) -> SorftimeResponse:
        """Fetch category trend data."""
        payload = {"nodeId": node_id, "trendIndex": trend_index}
        data = await self._post("CategoryTrend", domain, payload)
        return SorftimeResponse(**data)

    async def search_products(self, query_type: int, pattern: str, page: int = 1, domain: int = 1) -> SorftimeResponse:
        """Search for products."""
        payload = {
            "query": 1,
            "queryType": query_type,
            "pattern": pattern,
            "page": page
        }
        data = await self._post("ProductQuery", domain, payload)
        return SorftimeResponse(**data)

    async def search_keywords(self, keyword: str, page: int = 1, domain: int = 1) -> SorftimeResponse:
        """Search for keywords."""
        # Simplified pattern for test
        payload = {
            "pattern": {"keyword": keyword},
            "pageIndex": page,
            "pageSize": 20
        }
        data = await self._post("KeywordQuery", domain, payload)
        return SorftimeResponse(**data)

    async def fetch_keyword_details(self, keyword: str, domain: int = 1) -> SorftimeResponse:
        """Fetch details for a specific keyword."""
        payload = {"keyword": keyword}
        data = await self._post("KeywordRequest", domain, payload)
        return SorftimeResponse(**data)
