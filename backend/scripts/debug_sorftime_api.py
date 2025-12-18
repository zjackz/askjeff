import asyncio
import sys
import os

# Add current directory to sys.path so we can import app modules
sys.path.append(os.getcwd())

from app.services.sorftime.client import SorftimeClient

async def main():
    api_key = "uis1m3dyr0exaecvmmnnwlfzdvdkqt09"
    client = SorftimeClient(account_sk=api_key)
    asin = "B0FN44NCTQ"
    print(f"Checking ASIN: {asin}")
    
    try:
        response = await client.product_request(asin=asin, domain=1)
        print(f"Code: {response.code}")
        print(f"Msg: {response.message}")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
