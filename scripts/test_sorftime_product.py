import httpx
import json
import base64
import gzip
import io
from typing import Dict, Any, List, Optional

class SorftimeClient:
    BASE_URL = "https://standardapi.sorftime.com/api"
    
    def __init__(self, account_sk: str):
        self.account_sk = account_sk
        self.headers = {
            "Authorization": f"BasicAuth {self.account_sk}",
            "Content-Type": "application/json;charset=UTF-8"
        }

    def _decode_response(self, data: Any) -> Any:
        """
        Handle Gzip + Base64 decoding if applicable.
        The API doc says: "If gzip=1, returns base64 string. Need to base64 decode -> gzip decompress."
        However, sometimes the API might return raw JSON even if we didn't ask for gzip, 
        or we might want to support it explicitly.
        
        For this MVP, we'll assume standard JSON response unless we explicitly implement the gzip logic later.
        But if the data comes as a string that looks like base64, we might need to handle it.
        """
        return data

    async def fetch_product_details(self, asins: List[str], domain: int = 1, trend: int = 1) -> Dict[str, Any]:
        """
        Fetch product details for a list of ASINs.
        
        Args:
            asins: List of ASIN strings (max 10).
            domain: Domain ID (1=US, etc.).
            trend: 1 to include trend data, 2 to exclude.
        """
        url = f"{self.BASE_URL}/ProductRequest"
        params = {"domain": domain}
        
        # Construct payload
        # The doc says payload is an array of objects: [{ "ASIN": "...", "Trend": 1 }]
        # Or maybe just one object if single? Doc example shows array.
        # "多ASIN查询时，使用逗号分割',' 最多支持10个asin查询" -> Wait, the doc says "asin: String ... use comma to separate".
        # But the screenshot showed a JSON array body.
        # Let's follow the screenshot/doc structure which implies a JSON body.
        # Actually, the doc text says: "参数为JSON格式，使用body传参... 例如使用Postman请求CategoryRequest接口，设置body如下"
        # And for ProductRequest: "asin : String ... 多asin查询时，使用逗号分割"
        # This implies the body might be: { "asin": "A,B", "trend": 1 } OR [ { "asin": "A" }, { "asin": "B" } ]
        # The screenshot showed: [ { "ASIN": "...", "Trend": 1, ... } ]
        # Let's try the array format as it's more structured.
        
        payload = []
        # If the API expects a comma-separated string in a single object:
        # payload = { "ASIN": ",".join(asins), "Trend": trend }
        
        # If the API expects an array of objects (one per ASIN):
        for asin in asins:
            payload.append({
                "ASIN": asin,
                "Trend": trend
            })
            
        # Let's try the array format first as per the screenshot.
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, params=params, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()

async def main():
    # Account SK from the user's previous context/file
    # "vkf3v0wwt1zpyul3m2oxswszzky0zz09"
    ACCOUNT_SK = "vkf3v0wwt1zpyul3m2oxswszzky0zz09"
    
    client = SorftimeClient(ACCOUNT_SK)
    
    # Target ASIN from user request: B0C135XWWH
    target_asin = "B0C135XWWH"
    
    print(f"Fetching details for ASIN: {target_asin}...")
    try:
        result = await client.fetch_product_details([target_asin])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
