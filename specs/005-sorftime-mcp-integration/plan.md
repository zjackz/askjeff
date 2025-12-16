# 技术实施计划 - 需求 005

## 1. 技术栈

- **后端**: Python (FastAPI), `httpx` (异步 HTTP 客户端)
- **前端**: Vue 3, Element Plus
- **数据库**: PostgreSQL (复用现有模型)

## 2. 架构设计

### 2.1 后端架构

新增 `McpService` (`backend/app/services/mcp_service.py`) 负责与 Sorftime MCP 交互。

```python
class McpService:
    def __init__(self):
        self.base_url = "https://mcp.sorftime.com"
        self.api_key = "t1hsvi9nwjr1cwhgwwtmvevvwez4dz09"
    
    async def fetch_category_data(self, input_value: str) -> List[Dict]:
        # 1. 解析输入 (Input Resolver)
        # 2. 调用 MCP API
        # 3. 返回标准化数据
        pass
```

新增 API 路由 `backend/app/api/v1/endpoints/mcp.py`:
- `POST /mcp/fetch`: 接收输入，触发抓取任务。

### 2.2 数据流

1. **Frontend**: 用户输入 -> `POST /api/v1/mcp/fetch`
2. **Backend API**: 接收请求 -> 调用 `McpService.fetch_category_data`
3. **McpService**:
    - 调用 MCP 接口获取 JSON。
    - 数据清洗与映射 (Mapping MCP fields to AskJeff fields)。
    - 调用 `ImportService.import_data` (复用现有逻辑，模拟文件导入或直接传递 DataFrame)。
4. **Database**: 存储为 `Product` 记录。

### 2.3 关键挑战

- **字段映射**: MCP 返回的字段名可能与我们数据库字段不一致，需要建立映射表。
- **异步处理**: MCP 响应可能较慢，建议使用后台任务 (BackgroundTasks) 或直接异步等待（如果时间允许）。考虑到 Top 100 数据量不大，直接异步等待可能可行，但为了体验最好提供进度流。目前先采用简单的异步响应。

## 3. 接口定义

### MCP API (External)
- URL: `https://mcp.sorftime.com`
- Method: `GET` / `POST` (需确认具体 API 文档，假设通过 param 传递 key 和 query)
- Params: `key={api_key}`, `asin={asin}`, etc.

### Internal API
- `POST /api/v1/mcp/fetch`
  - Request: `{ "input": "B08XXXXXXX", "type": "asin" }`
  - Response: `{ "status": "success", "imported_count": 100, "batch_id": "..." }`

## 4. 实施步骤

1. **探索 MCP API**: 编写脚本测试 MCP 接口，确认输入输出格式。
2. **后端开发**: 实现 `McpService` 和 API。
3. **对接导入**: 将 MCP 数据转换为 `ImportService` 可接受的格式。
4. **前端开发**: 添加 UI 入口。
