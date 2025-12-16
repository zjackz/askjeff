import httpx
import asyncio
import json
import os
from datetime import datetime

# Configuration
API_URL = "http://localhost:8001/api/mcp/fetch"
TARGET_URL = "https://www.amazon.com/gp/bestsellers/sporting-goods/16062041/ref=pd_zg_hrsr_sporting-goods"
REPORT_FILE = "specs/005-sorftime-mcp-integration/test_report_bestsellers.md"

async def run_test():
    report_lines = []
    report_lines.append(f"# MCP Full Flow Test Report: Amazon Bestsellers")
    report_lines.append(f"**Date:** {datetime.now().isoformat()}")
    report_lines.append(f"**Target URL:** `{TARGET_URL}`")
    report_lines.append(f"**API Endpoint:** `{API_URL}`")
    report_lines.append("")

    print("Starting test...")
    
    # 1. Prepare Request
    payload = {
        "input": TARGET_URL,
        "type": "auto" # Let the backend auto-detect
    }
    report_lines.append("## 1. Request Payload")
    report_lines.append("```json")
    report_lines.append(json.dumps(payload, indent=2))
    report_lines.append("```")
    
    # 2. Send Request
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            start_time = datetime.now()
            print(f"Sending POST request to {API_URL}...")
            resp = await client.post(API_URL, json=payload)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            report_lines.append(f"## 2. Response (Duration: {duration:.2f}s)")
            report_lines.append(f"**Status Code:** {resp.status_code}")
            
            try:
                data = resp.json()
                report_lines.append("### Response Body")
                report_lines.append("```json")
                report_lines.append(json.dumps(data, indent=2))
                report_lines.append("```")
                
                if resp.status_code == 200 and data.get("status") == "success":
                    print("Request successful!")
                    # 3. Verify File Download
                    # The response message usually contains "Import Batch ID: X"
                    # We can try to list imports to find the latest one
                    pass
                else:
                    print(f"Request failed with status {resp.status_code}")
                    
            except json.JSONDecodeError:
                report_lines.append("### Raw Response Body (Not JSON)")
                report_lines.append(f"```\n{resp.text}\n```")

        except Exception as e:
            report_lines.append(f"## Error")
            report_lines.append(f"Exception occurred: {str(e)}")
            print(f"Error: {e}")

    # 3. Save Report
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(report_lines))
    
    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_test())
