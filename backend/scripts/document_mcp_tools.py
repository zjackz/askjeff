import httpx
import asyncio
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "https://mcp.sorftime.com"
API_KEY = "t1hsvi9nwjr1cwhgwwtmvevvwez4dz09"
REPORT_FILE = "specs/005-sorftime-mcp-integration/mcp_tools_report.md"

async def run():
    report_lines = []
    report_lines.append(f"# MCP Tools Interface Documentation")
    report_lines.append(f"**Date:** {datetime.now().isoformat()}")
    report_lines.append(f"**Base URL:** `{BASE_URL}`")
    report_lines.append("")

    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        # 1. Initialize
        report_lines.append("## 1. Initialization")
        init_url = f"{BASE_URL}?key={API_KEY}"
        init_payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "askjeff-doc", "version": "1.0"}
            },
            "id": 1
        }
        report_lines.append("### Request")
        report_lines.append("```json")
        report_lines.append(json.dumps(init_payload, indent=2))
        report_lines.append("```")

        print("Initializing...")
        resp = await client.post(init_url, json=init_payload)
        report_lines.append("### Response")
        report_lines.append(f"Status: {resp.status_code}")
        try:
            # Parse SSE for initialize (though usually it returns JSON directly or SSE)
            # Sorftime seems to return SSE even for init sometimes, or just 200 OK
            if "data:" in resp.text:
                 report_lines.append("```")
                 report_lines.append(resp.text)
                 report_lines.append("```")
            else:
                 report_lines.append("```json")
                 report_lines.append(json.dumps(resp.json(), indent=2))
                 report_lines.append("```")
        except:
            report_lines.append(f"Raw: {resp.text}")

        # 2. List Tools
        report_lines.append("## 2. List Tools (`tools/list`)")
        list_payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        report_lines.append("### Request")
        report_lines.append("```json")
        report_lines.append(json.dumps(list_payload, indent=2))
        report_lines.append("```")

        print("Listing tools...")
        resp = await client.post(init_url, json=list_payload)
        
        report_lines.append("### Response")
        report_lines.append(f"Status: {resp.status_code}")
        
        tools_data = None
        # Parse SSE
        for line in resp.text.splitlines():
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "result" in data:
                        tools_data = data["result"]
                        report_lines.append("#### Parsed Result")
                        report_lines.append("```json")
                        report_lines.append(json.dumps(tools_data, indent=2, ensure_ascii=False))
                        report_lines.append("```")
                except:
                    pass
        
        if not tools_data:
             report_lines.append("#### Raw Response")
             report_lines.append("```")
             report_lines.append(resp.text)
             report_lines.append("```")

    # 3. Save Report
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(report_lines))
    
    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    asyncio.run(run())
