# API 使用示例

本文档提供 ASKJeff 系统所有主要 API 的使用示例。

## 基础信息

- **Base URL**: `http://localhost:8001`
- **API 文档**: `http://localhost:8001/docs`
- **认证方式**: JWT Bearer Token

## 认证

### 登录获取 Token

**默认账号**:
- 管理员: `admin` / `admin666`
- 运营人员: `shangu` / `shangu666`

```bash
curl -X POST "http://localhost:8001/api/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin666"
```

**响应**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 使用 Token

在后续请求中添加 Authorization 头：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8001/api/..."
```

## 导入功能

### 1. 上传文件导入

```bash
curl -X POST "http://localhost:8001/api/imports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@products.csv" \
  -F "importStrategy=append"
```

**参数**:
- `file`: CSV 或 XLSX 文件
- `importStrategy`: `append`（追加）或 `replace`（替换）
- `sheetName`: (可选) Excel 工作表名称

**响应**:

```json
{
  "id": 1,
  "filename": "products.csv",
  "status": "succeeded",
  "total_rows": 100,
  "success_rows": 95,
  "failed_rows": 5,
  "created_at": "2025-12-04T10:00:00Z"
}
```

### 2. 查询导入列表

```bash
curl "http://localhost:8001/api/imports?page=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**查询参数**:
- `page`: 页码（默认 1）
- `pageSize`: 每页数量（默认 20）
- `status`: 筛选状态（`pending`, `succeeded`, `failed`）
- `asin`: 按 ASIN 搜索

**响应**:

```json
{
  "items": [
    {
      "id": 1,
      "filename": "products.csv",
      "status": "succeeded",
      "total_rows": 100,
      "created_at": "2025-12-04T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 3. 查询导入详情

```bash
curl "http://localhost:8001/api/imports/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**:

```json
{
  "batch": {
    "id": 1,
    "filename": "products.csv",
    "status": "succeeded",
    "total_rows": 100,
    "success_rows": 95,
    "failed_rows": 5,
    "failure_summary": {
      "items": [
        {
          "row": 10,
          "reason": "缺少必需字段: price"
        }
      ]
    }
  },
  "failed_rows": [...]
}
```

## AI 特征提取

### 1. 启动批次提取

```bash
curl -X POST "http://localhost:8001/api/imports/1/extract" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_fields": ["brand", "material", "size"]
  }'
```

**响应**:

```json
{
  "message": "Extraction started",
  "batch_id": 1
}
```

### 2. 查询提取运行记录

```bash
curl "http://localhost:8001/api/imports/1/runs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**:

```json
{
  "items": [
    {
      "id": 1,
      "batch_id": 1,
      "target_fields": ["brand", "material"],
      "status": "completed",
      "total_items": 100,
      "processed_items": 100,
      "total_tokens": 15000,
      "total_cost": 0.045,
      "created_at": "2025-12-04T10:00:00Z"
    }
  ]
}
```

### 3. 查询提取任务列表

```bash
curl "http://localhost:8001/api/extraction?page=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 聊天问答

### 1. 发送问题

```bash
curl -X POST "http://localhost:8001/api/chat/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "有多少个产品？"
  }'
```

**响应**:

```json
{
  "answer": "当前系统中共有 1,234 个产品。",
  "references": [
    {
      "data": {
        "count": 1234
      }
    }
  ],
  "session_id": 1
}
```

### 2. 查询历史记录

```bash
curl "http://localhost:8001/api/chat/history?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**:

```json
{
  "items": [
    {
      "id": 1,
      "question": "有多少个产品？",
      "answer": "当前系统中共有 1,234 个产品。",
      "created_at": "2025-12-04T10:00:00Z"
    }
  ]
}
```

## 数据导出

### 1. 创建导出任务

```bash
curl -X POST "http://localhost:8001/api/exports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exportType": "clean-products",
    "filters": {
      "batch_id": 1
    },
    "selectedFields": ["asin", "title", "price"],
    "fileFormat": "csv"
  }'
```

**参数**:
- `exportType`: `clean-products`（清洗后数据）或 `extraction_results`（AI 提取结果）
- `filters`: 筛选条件
  - `batch_id`: 批次 ID
  - `run_id`: 提取运行 ID（导出 AI 结果时必需）
- `selectedFields`: 要导出的字段列表
- `fileFormat`: `csv` 或 `xlsx`

**响应**:

```json
{
  "id": 1,
  "export_type": "clean_products",
  "status": "succeeded",
  "file_format": "csv",
  "file_path": "/app/storage/exports/1.csv",
  "started_at": "2025-12-04T10:00:00Z",
  "finished_at": "2025-12-04T10:00:05Z"
}
```

### 2. 查询导出任务

```bash
curl "http://localhost:8001/api/exports/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 下载导出文件

```bash
curl "http://localhost:8001/api/exports/1/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o export.csv
```

### 4. 查询导出历史

```bash
curl "http://localhost:8001/api/exports?limit=20&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 产品查询

### 1. 查询产品列表

```bash
curl "http://localhost:8001/api/products?page=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**查询参数**:
- `page`: 页码
- `pageSize`: 每页数量
- `asin`: ASIN 搜索
- `title`: 标题搜索
- `minPrice`: 最低价格
- `maxPrice`: 最高价格
- `minRating`: 最低评分
- `category`: 分类筛选

**响应**:

```json
{
  "items": [
    {
      "id": 1,
      "asin": "B001",
      "title": "Product Title",
      "price": 29.99,
      "currency": "USD",
      "rating": 4.5,
      "reviews": 100,
      "category": "Electronics"
    }
  ],
  "total": 1234,
  "page": 1,
  "page_size": 20
}
```

### 2. 查询单个产品

```bash
curl "http://localhost:8001/api/products/B001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 健康检查

### 系统健康状态

```bash
curl "http://localhost:8001/health"
```

**响应**:

```json
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "storage": "healthy",
    "deepseek_config": "configured"
  }
}
```

## 错误处理

所有 API 错误响应格式：

```json
{
  "detail": "错误描述",
  "code": "ERROR_CODE",
  "details": {
    "field": "additional info"
  }
}
```

**常见错误码**:
- `401`: 未授权（Token 无效或过期）
- `403`: 禁止访问
- `404`: 资源不存在
- `422`: 验证错误
- `500`: 服务器内部错误

## Python 客户端示例

```python
import requests

class ASKJeffClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        """登录获取 Token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token
    
    def _headers(self):
        """获取请求头"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def upload_file(self, file_path, strategy="append"):
        """上传文件导入"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"importStrategy": strategy}
            response = requests.post(
                f"{self.base_url}/api/imports",
                headers=self._headers(),
                files=files,
                data=data
            )
        response.raise_for_status()
        return response.json()
    
    def ask_question(self, question):
        """发送问题"""
        response = requests.post(
            f"{self.base_url}/api/chat/ask",
            headers=self._headers(),
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()
    
    def export_data(self, export_type, filters, fields, format="csv"):
        """导出数据"""
        response = requests.post(
            f"{self.base_url}/api/exports",
            headers=self._headers(),
            json={
                "exportType": export_type,
                "filters": filters,
                "selectedFields": fields,
                "fileFormat": format
            }
        )
        response.raise_for_status()
        return response.json()

# 使用示例
client = ASKJeffClient()
client.login("admin", "admin123")

# 上传文件
batch = client.upload_file("products.csv")
print(f"导入批次 ID: {batch['id']}")

# 问答
answer = client.ask_question("有多少个产品？")
print(f"回答: {answer['answer']}")

# 导出
job = client.export_data(
    export_type="clean-products",
    filters={"batch_id": batch["id"]},
    fields=["asin", "title", "price"],
    format="csv"
)
print(f"导出任务 ID: {job['id']}")
```

## 更多信息

- 完整 API 文档: <http://localhost:8001/docs>
- OpenAPI Schema: <http://localhost:8001/openapi.json>
