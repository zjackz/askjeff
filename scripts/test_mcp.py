import httpx
import asyncio
import json

API_KEY = "t1hsvi9nwjr1cwhgwwtmvevvwez4dz09"
BASE_URL = "https://mcp.sorftime.com"

async def test_mcp():
    async with httpx.AsyncClient() as client:
        # Test 1: Base URL with key
        print(f"--- Testing Base URL ---")
        try:
            resp = await client.get(f"{BASE_URL}?key={API_KEY}")
            print(f"Status: {resp.status_code}")
            try:
                print(f"Response: {json.dumps(resp.json(), indent=2)[:500]}...")
            except:
                print(f"Response Text: {resp.text[:500]}...")
        except Exception as e:
            print(f"Error: {e}")

        # Test 2: Search by ASIN (assuming parameter 'asin' or 'q')
        # Using a random real ASIN (e.g. Anker Charger B07GQJZK2S)
        asin = "B07GQJZK2S"
        print(f"\n--- Testing ASIN Search: {asin} ---")
        try:
            # Try 'asin' param
            resp = await client.get(f"{BASE_URL}?key={API_KEY}&asin={asin}")
            if resp.status_code == 200:
                print(f"Status: {resp.status_code}")
                print(f"Response: {json.dumps(resp.json(), indent=2)[:500]}...")
            else:
                # Try 'q' param
                print("Retrying with 'q' param...")
                resp = await client.get(f"{BASE_URL}?key={API_KEY}&q={asin}")
                print(f"Status: {resp.status_code}")
                try:
                    print(f"Response: {json.dumps(resp.json(), indent=2)[:500]}...")
                except:
                    print(f"Response Text: {resp.text[:500]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp())
