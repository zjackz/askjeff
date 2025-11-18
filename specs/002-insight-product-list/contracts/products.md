# API 契约：产品列表与 chat 交互

> 说明：复用现有后端产品数据源，仅定义前端所需的查询/详情与 chat 交互格式。字段名保持后端现状，若需调整需同步版本化。

## GET /api/products
- **用途**：获取产品列表，支持筛选、排序、分页。
- **Query 参数**：
  - `batch_id`（string，可选）
  - `asin_keyword`（string，可选，匹配 ASIN/标题模糊）
  - `status`（string，可选，例如 success/failed/pending）
  - `updated_from` / `updated_to`（ISO8601，可选）
  - `page`（int，默认 1）
  - `page_size`（int，默认 20，最大 100）
  - `sort_by`（string，可选：`last_updated_at`/`status`/`asin` 等）
  - `sort_order`（string，可选：`asc`/`desc`，默认 desc）
- **响应 200**：
  ```json
  {
    "items": [
      {
        "id": "string",
        "asin": "B000000",
        "title": "示例产品",
        "batch_id": "batch-001",
        "status": "success",
        "last_updated_at": "2025-11-18T12:00:00Z",
        "metrics": {
          "price": 19.9,
          "sales": 120,
          "rating": 4.6
        },
        "failure_reason": null
      }
    ],
    "page": 1,
    "page_size": 20,
    "total": 123
  }
  ```
- **错误**：400（参数非法），500（服务异常）。

## GET /api/products/{id}
- **用途**：获取单个产品的详情（用于行详情弹窗）。
- **路径参数**：`id`（string）
- **响应 200**：与列表单项字段一致，可补充后台已有扩展字段。
- **错误**：404（不存在），500。

## POST /api/chat/messages
- **用途**：发送 chat 问题并获取回复（同步响应模式）。
- **Body**：
  ```json
  {
    "session_id": "uuid-optional",
    "question": "string"
  }
  ```
- **响应 200**：
  ```json
  {
    "session_id": "uuid-optional",
    "answer": "string",
    "status": "success",
    "error_message": null
  }
  ```
- **错误**：429（限流）、502（上游不可用）、500。

> 若后端已有等价接口且路径不同，应在实现前确认并对前端适配，确保契约与实际一致。
