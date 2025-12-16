import httpx
import asyncio
import json

BASE_URL = "http://localhost:8001/api/mcp/fetch"

async def test_endpoint():
    print(f"Testing MCP Endpoint: {BASE_URL}")
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test 1: Keyword Search (should work)
        print("\n--- Test 1: Keyword 'anker charger' ---")
        payload = {
            "input": "anker charger",
            "type": "keyword"
        }
        try:
            resp = await client.post(BASE_URL, json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Response: {json.dumps(resp.json(), indent=2)[:500]}...")
        except Exception as e:
            print(f"Error: {e}")

        # Test 2: ASIN (might fail if not found)
        print("\n--- Test 2: ASIN 'B07GQJZK2S' ---")
        payload = {
            "input": "B07GQJZK2S",
            "type": "asin"
        }
        try:
            resp = await client.post(BASE_URL, json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Response: {json.dumps(resp.json(), indent=2)[:500]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
