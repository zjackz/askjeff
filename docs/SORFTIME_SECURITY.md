# Sorftime API 安全配置指南

## 🔐 API Key 管理

### 环境变量配置

**后端配置** (`backend/.env`):

```bash
SORFTIME_API_KEY=your_actual_api_key_here
```

**前端配置** (`frontend/.env`):

```bash
VITE_SORFTIME_API_KEY=your_actual_api_key_here
```

⚠️ **重要**: 
- 永远不要将 API Key 提交到 Git 仓库
- 使用 `.gitignore` 排除 `.env` 文件
- 在生产环境使用环境变量或密钥管理服务

### 获取 API Key

1. 登录 Sorftime 控制台
2. 进入"API 管理"页面
3. 生成或复制您的 API Key
4. 将 Key 保存到环境变量中

### 在代码中使用

**后端 (Python)**:

```python
import os
from app.services.sorftime import SorftimeClient

# 从环境变量读取
api_key = os.getenv("SORFTIME_API_KEY")
if not api_key:
    raise ValueError("SORFTIME_API_KEY environment variable not set")

client = SorftimeClient(account_sk=api_key)
```

**前端 (TypeScript)**:

```typescript
// 从环境变量读取（仅用于开发/测试）
const apiKey = (import.meta as any).env.VITE_SORFTIME_API_KEY

// ⚠️ 生产环境应通过后端代理，不要在前端暴露 API Key
```

---

## 🛡️ 安全最佳实践

### 1. 使用后端代理

**推荐架构**:

```
Frontend → Backend API → Sorftime API
```

**优势**:
- API Key 不暴露给客户端
- 统一的错误处理和日志
- 可以添加访问控制和速率限制
- 便于缓存和优化

**实现示例**:

```python
# backend/app/api/v1/endpoints/sorftime.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.sorftime import SorftimeClient
from app.core.config import settings

router = APIRouter()

def get_sorftime_client():
    return SorftimeClient(account_sk=settings.SORFTIME_API_KEY)

@router.post("/product")
async def get_product(
    asin: str,
    client: SorftimeClient = Depends(get_sorftime_client)
):
    """代理产品查询请求"""
    try:
        response = await client.product_request(asin=asin, domain=1)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. 访问控制

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """验证管理员权限"""
    token = credentials.credentials
    # 实现您的 token 验证逻辑
    if not is_valid_admin_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return token

@router.post("/product")
async def get_product(
    asin: str,
    admin_token: str = Depends(verify_admin),
    client: SorftimeClient = Depends(get_sorftime_client)
):
    """需要管理员权限的端点"""
    response = await client.product_request(asin=asin, domain=1)
    return response
```

### 3. 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/product")
@limiter.limit("60/minute")  # 每分钟最多 60 次请求
async def get_product(
    request: Request,
    asin: str,
    client: SorftimeClient = Depends(get_sorftime_client)
):
    response = await client.product_request(asin=asin, domain=1)
    return response
```

### 4. 请求日志和审计

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def log_api_request(
    user_id: str,
    endpoint: str,
    params: dict,
    response_code: int
):
    """记录 API 请求用于审计"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "endpoint": endpoint,
        "params": params,
        "response_code": response_code
    }
    logger.info(f"API Request: {log_entry}")
    # 可选：保存到数据库用于审计
```

---

## 🔄 API Key 轮换

### 定期轮换策略

1. **生成新 Key**
   - 在 Sorftime 控制台生成新的 API Key
   
2. **更新环境变量**

   ```bash
   # 更新生产环境
   export SORFTIME_API_KEY=new_api_key_here
   ```

3. **重启服务**

   ```bash
   # Docker 环境
   docker-compose restart backend
   ```

4. **验证新 Key**
   - 测试几个 API 调用确保正常工作
   
5. **撤销旧 Key**
   - 在 Sorftime 控制台撤销旧的 API Key

### 自动化轮换（高级）

```python
# 使用密钥管理服务（如 AWS Secrets Manager）
import boto3

def get_api_key_from_secrets_manager():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='sorftime/api-key')
    return response['SecretString']

# 在应用启动时获取
api_key = get_api_key_from_secrets_manager()
sorftime_client = SorftimeClient(account_sk=api_key)
```

---

## 📊 监控和告警

### 配额监控

```python
async def check_quota():
    """定期检查 API 配额"""
    client = SorftimeClient(account_sk=os.getenv("SORFTIME_API_KEY"))
    
    # 查询剩余 request
    request_info = await client.request_stream(domain=1)
    remaining = request_info.data.get('remainingRequests', 0)
    
    # 查询剩余积分
    coin_info = await client.coin_query(domain=1)
    remaining_coins = coin_info.data.get('remainingCoins', 0)
    
    # 告警阈值
    if remaining < 1000:
        send_alert(f"Sorftime request quota low: {remaining} remaining")
    
    if remaining_coins < 100:
        send_alert(f"Sorftime coins low: {remaining_coins} remaining")
```

### 错误率监控

```python
from prometheus_client import Counter, Histogram

# Prometheus 指标
api_requests_total = Counter(
    'sorftime_api_requests_total',
    'Total Sorftime API requests',
    ['endpoint', 'status']
)

api_request_duration = Histogram(
    'sorftime_api_request_duration_seconds',
    'Sorftime API request duration',
    ['endpoint']
)

async def monitored_api_call(endpoint: str, **kwargs):
    """带监控的 API 调用"""
    start_time = time.time()
    
    try:
        response = await client._post(endpoint, **kwargs)
        status = 'success' if response.code == 0 else 'error'
        api_requests_total.labels(endpoint=endpoint, status=status).inc()
        return response
    finally:
        duration = time.time() - start_time
        api_request_duration.labels(endpoint=endpoint).observe(duration)
```

---

## 🚨 应急响应

### API Key 泄露处理流程

1. **立即撤销泄露的 Key**
   - 登录 Sorftime 控制台
   - 撤销受影响的 API Key

2. **生成新 Key**
   - 生成新的 API Key
   - 更新所有环境的配置

3. **审计使用记录**
   - 检查 API 使用日志
   - 确认是否有异常调用

4. **通知相关人员**
   - 通知团队成员
   - 记录事件详情

5. **改进安全措施**
   - 审查代码，确保没有硬编码 Key
   - 加强访问控制
   - 实施更严格的监控

---

## ✅ 安全检查清单

- [ ] API Key 存储在环境变量中，未硬编码
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 生产环境使用后端代理，不在前端暴露 Key
- [ ] 实施了访问控制和身份验证
- [ ] 配置了速率限制
- [ ] 启用了请求日志和审计
- [ ] 设置了配额监控和告警
- [ ] 制定了 Key 轮换计划
- [ ] 准备了应急响应流程
- [ ] 定期审查安全配置

---

## 📚 相关文档

- [Sorftime API 使用指南](./SORFTIME_USAGE_GUIDE.md)
- [API 文档](./sorftimeAMAZON APIS.TXT)
- [后端客户端代码](../backend/app/services/sorftime/client.py)
- [前端类型定义](../frontend/src/types/sorftime.ts)
