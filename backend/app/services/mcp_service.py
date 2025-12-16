import httpx
import logging
import json
import asyncio
import os
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class McpService:
    def __init__(self):
        self.base_url = "https://mcp.sorftime.com"
        self.api_key = "t1hsvi9nwjr1cwhgwwtmvevvwez4dz09"
        self.client_info = {"name": "askjeff", "version": "0.1.0"}
        self.initialized = False
        # Allow disabling real calls via env var
        self.mock_mode = os.getenv("MOCK_MCP", "false").lower() == "true"

    async def fetch_category_data(self, input_value: str, input_type: str = "auto") -> List[Dict]:
        """
        Fetch category data from Sorftime MCP.
        
        Args:
            input_value: ASIN, URL, or Keyword
            input_type: 'asin', 'url', 'keyword', 'nodeId', or 'auto'
        """
        logger.info(f"Fetching MCP data for input: {input_value} (type: {input_type})")
        
        if self.mock_mode:
            logger.info("MOCK_MCP is enabled, returning mock data")
            return self._get_mock_data(input_value)
        
        async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
            # 1. Initialize Session
            await self._initialize(client)
            
            # 2. Determine arguments for category_more_poroducts
            tool_name = "category_more_poroducts" # Note the typo in tool name
            arguments = {"amzSite": "US"}
            
            # Handle Auto-detection
            if input_type == "auto":
                if input_value.startswith("http"):
                    input_type = "url"
                elif input_value.startswith("B0") and len(input_value) == 10:
                    input_type = "asin"
                elif input_value.isdigit():
                    input_type = "nodeId"
                else:
                    input_type = "keyword"
            
            # Process input based on type
            if input_type == "url":
                # Extract ASIN or NodeID from URL
                import re
                asin_match = re.search(r'/([A-Z0-9]{10})(?:[/?]|$)', input_value)
                if asin_match:
                    arguments["asin"] = asin_match.group(1)
                else:
                    # Try Node ID
                    node_match = re.search(r'node=(\d+)', input_value)
                    if node_match:
                        arguments["nodeId"] = node_match.group(1)
                    else:
                        # Try Bestsellers URL format: .../bestsellers/category/123456/...
                        bs_match = re.search(r'/bestsellers/[^/]+/(\d+)', input_value)
                        if bs_match:
                            arguments["nodeId"] = bs_match.group(1)
                        else:
                            # Fallback to keyword search if URL parsing fails? 
                            # Or just treat the whole URL as a keyword (bad idea).
                            # Let's error or try keyword.
                            logger.warning(f"Could not parse ASIN/Node from URL: {input_value}")
                            arguments["keyword"] = input_value # Fallback
            
            elif input_type == "asin":
                arguments["asin"] = input_value
            
            elif input_type == "nodeId":
                arguments["nodeId"] = input_value
                
            else: # keyword
                arguments["keyword"] = input_value

            # 3. Call Tool
            logger.info(f"Calling tool {tool_name} with args: {arguments}")
            result = await self._call_tool(client, tool_name, arguments)
            
            # 4. Process Result
            return self._process_result(result)

    async def _initialize(self, client: httpx.AsyncClient):
        """Send JSON-RPC initialize request."""
        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": self.client_info
            },
            "id": 1
        }
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            logger.error(f"MCP Initialize failed: {resp.status_code} {resp.text}")
            # We continue anyway as some servers might be stateless or already init
        else:
            logger.debug("MCP Initialized")

    async def _call_tool(self, client: httpx.AsyncClient, name: str, arguments: Dict) -> Any:
        """Call a tool via JSON-RPC over POST-SSE."""
        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            },
            "id": 2 # Increment ID if needed
        }
        
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            raise Exception(f"Tool call failed with status {resp.status_code}: {resp.text}")
            
        # Parse SSE-like response
        return self._parse_sse_response(resp.text)

    def _get_mock_data(self, input_value: str) -> List[Dict]:
        """Return mock data for testing."""
        # Generate 10 mock items
        mock_items = []
        for i in range(1, 11):
            mock_items.append({
                "asin": f"B08MOCK{i:03d}",
                "title": f"Mock Product {i} for {input_value}",
                "price": 19.99 + i,
                "currency": "USD",
                "sales_rank": i,
                "reviews": 100 * i,
                "rating": 4.5,
                "category": "Mock Category",
                "image_url": "https://via.placeholder.com/150",
                "raw_data": {}
            })
        return mock_items

    def _parse_sse_response(self, text: str) -> Any:
        """Parse the 'data: ...' line from the response body."""
        for line in text.splitlines():
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "error" in data:
                        raise Exception(f"MCP Error: {data['error']}")
                    if "result" in data:
                        return data["result"]
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON from SSE line: {line}")
                    continue
        raise Exception("No valid JSON-RPC data found in response")

    def _process_result(self, result: Dict) -> List[Dict]:
        """Convert tool result content to list of dicts."""
        if not result or "content" not in result:
            return []
            
        content_list = result["content"]
        items = []
        
        for content in content_list:
            if content["type"] == "text":
                text = content["text"]
                print(f"DEBUG: Tool returned text content (len={len(text)}): {text[:500]}...", flush=True)
                logger.info(f"Tool returned text content (len={len(text)}): {text[:500]}...")
                try:
                    # The tool returns a JSON string representing a list of products
                    products = json.loads(text)
                    if isinstance(products, list):
                        items.extend(products)
                    elif isinstance(products, dict):
                        items.append(products)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse content text as JSON")
                    continue
                    
        # Normalize items to match our schema
        normalized_items = []
        for item in items:
            # Map fields
            # Map fields
            # Handle Chinese keys from Sorftime
            normalized = {
                "asin": item.get("asin") or item.get("ASIN") or item.get("产品ASIN码"),
                "title": item.get("title") or item.get("Title") or item.get("productName") or item.get("产品标题") or item.get("商品标题") or item.get("标题") or item.get("产品名称"),
                "price": item.get("price") or item.get("Price") or item.get("价格") or item.get("售价"),
                "currency": item.get("currency") or "USD",
                "sales_rank": item.get("rank") or item.get("salesRank") or item.get("大类排名") or item.get("小类排名") or item.get("排名"),
                "reviews": item.get("reviewsCount") or item.get("reviews") or item.get("评论数") or item.get("留评数"),
                "rating": item.get("rating") or item.get("score") or item.get("评分") or item.get("星级"),
                "category": item.get("category") or item.get("nodePath") or item.get("类目路径"),
                "image_url": item.get("imageUrl") or item.get("image") or item.get("主图链接") or item.get("图片链接"),
                # Keep raw data for reference
                "raw_data": item 
            }
            normalized_items.append(normalized)
            
        return normalized_items

mcp_service = McpService()
