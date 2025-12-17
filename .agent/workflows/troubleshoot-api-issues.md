---
description: 通过日志系统排查 API 调用问题的标准流程
---

# API 问题排查流程

## 前提条件
- 系统已启用日志监控功能
- 所有外部 API 调用都通过统一的 Client 并记录日志
- 日志包含：平台、URL、请求、响应、状态码、耗时、Quota 等信息

## 🚀 快速开始：自动化分析（推荐）

### 方法一：使用自动化分析工具

```bash
# 分析最近 60 分钟的所有 API 调用
docker exec askjeff-dev-backend-1 python analyze_api_logs.py

# 分析最近 30 分钟的日志
docker exec askjeff-dev-backend-1 python analyze_api_logs.py --minutes 30

# 只分析 Sorftime 平台的调用
docker exec askjeff-dev-backend-1 python analyze_api_logs.py --platform Sorftime

# 分析更多日志（默认 50 条）
docker exec askjeff-dev-backend-1 python analyze_api_logs.py --limit 100
```

**工具会自动输出：**
- ✅ 成功/失败统计
- 📊 按平台、端点的分布
- ⏱️ 平均响应时间
- 💰 Quota 消耗情况
- ❌ 错误详情和分类
- 💡 诊断建议

**示例输出：**

```
================================================================================
📊 API 调用日志分析报告
================================================================================
时间范围: 最近 60 分钟
日志总数: 15
================================================================================

📈 统计概览
  ✅ 成功: 10 (66.7%)
  ❌ 失败: 5 (33.3%)
  ⏱️  平均耗时: 3245ms
  💰 Quota 消耗: 25
  💰 Quota 剩余: 3769

🌐 按平台统计
  Sorftime: 15

🔗 按端点统计
  CategoryRequest: 8
  ProductRequest: 7

❌ 错误详情 (共 5 条)
--------------------------------------------------------------------------------

[1] 19:25:30 - Sorftime API CategoryRequest
    平台: Sorftime
    URL: https://standardapi.sorftime.com/api/CategoryRequest?domain=1
    状态码: 200
    耗时: 5085ms
    错误码: None
    错误信息: None
    请求参数: {'nodeId': '678542011', 'queryStart': None, 'queryDate': None}
    原始响应: {"RequestLeft":3794,"RequestConsumed":5,"Code":0,"Message":null...

================================================================================
💡 诊断建议
================================================================================
🔍 发现响应解析失败:
   1. 检查 Pydantic 模型字段映射
   2. 查看 raw_response 了解实际响应结构
   3. 确认字段名大小写是否匹配
================================================================================
```

### 方法二：手动查看日志监控页面

```
路径：系统菜单 -> 日志中心
切换到：API 调用 Tab
```

### 2. 筛选相关日志
- **时间范围**：选择问题发生的时间段
- **级别筛选**：
  - 先查看 `error` 级别，定位失败的调用
  - 再查看 `info` 级别，对比成功的调用
- **关键字搜索**：输入 ASIN、batch_id、endpoint 名称等

### 3. 查看日志详情
点击"查看"按钮，重点关注：

#### 3.1 基本信息

```json
{
  "platform": "Sorftime/DeepSeek/...",
  "url": "完整的 API URL",
  "method": "POST/GET",
  "status_code": 200/400/500,
  "duration_ms": 响应时间
}
```

#### 3.2 请求信息

```json
{
  "request": {
    // 检查参数是否正确
    // 检查必填字段是否缺失
  }
}
```

#### 3.3 响应信息

```json
{
  "response": {
    "code": 0/非0,  // API 业务状态码
    "message": "错误信息",
    "requestLeft": 剩余额度,
    "requestConsumed": 消耗额度
  }
}
```

### 4. 问题分类和处理

#### 类型 A：HTTP 状态码异常（4xx/5xx）
**症状**：`status_code` 不是 200
**可能原因**：
- 401/403：API Key 无效或权限不足
- 404：URL 错误或资源不存在
- 429：请求频率超限
- 500：服务器内部错误

**排查步骤**：
1. 检查 API Key 配置（`backend/app/config.py`）
2. 检查 URL 拼接逻辑
3. 检查请求频率和重试策略
4. 联系 API 提供方

#### 类型 B：业务状态码异常（code != 0）
**症状**：`status_code` 是 200，但 `response.code != 0`
**可能原因**：
- 参数不合法（如：类目 ID 无效）
- Quota 不足
- 数据不存在

**排查步骤**：
1. 查看 `response.message` 了解具体错误
2. 检查 `request` 参数是否正确
3. 检查 `requestLeft` 是否为 0
4. 尝试用不同参数重试

#### 类型 C：响应解析失败
**症状**：所有 `response` 字段都是 `null`
**可能原因**：
- API 返回的 JSON 结构与模型不匹配
- 字段名大小写不一致
- 数据类型不匹配

**排查步骤**：
1. 查看日志中的 `raw_response`（如果有）
2. 使用调试脚本直接调用 API，查看原始响应
3. 对比 Pydantic 模型定义和实际响应
4. 修复字段映射或添加 `AliasChoices`

**调试脚本模板**：

```python
# backend/debug_api.py
import asyncio
import httpx
import json

async def test_api():
    url = "API_URL"
    headers = {"Authorization": "..."}
    payload = {...}
    
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)[:2000]}")

asyncio.run(test_api())
```

#### 类型 D：数据为空但无错误
**症状**：`code=0`，但返回的数据列表为空
**可能原因**：
- 查询条件过于严格，确实没有数据
- 数据结构嵌套层级不对
- 字段名不匹配（如 `Products` vs `products`）

**排查步骤**：
1. 检查业务逻辑：该查询是否应该有数据
2. 查看完整的 `response.data` 结构
3. 检查代码中的数据提取逻辑（如 `data.get("products")`）
4. 添加调试日志打印 `data.keys()`

### 5. 修复验证

修复代码后：
1. 重启后端服务
2. 重新触发相同操作
3. 查看日志确认：
   - 级别变为 `info`
   - `response.code = 0`
   - 数据正确返回
4. 验证业务功能正常

## 日志记录最佳实践

### 对于开发者

#### 1. 记录关键节点

```python
logger.info(f"开始处理批次 {batch_id}")
logger.info(f"调用 API: {endpoint}, 参数: {params}")
logger.info(f"API 返回: code={response.code}, 数据量={len(data)}")
logger.info(f"处理完成: 成功={success}, 失败={failed}")
```

#### 2. 记录异常详情

```python
try:
    result = await process()
except Exception as e:
    logger.error(f"处理失败: {e}", exc_info=True, extra={
        "batch_id": batch_id,
        "input": input_value,
        "step": "fetch_bestsellers"
    })
    raise
```

#### 3. 记录数据结构

```python
logger.debug(f"Response data type: {type(data)}")
logger.debug(f"Response keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
logger.debug(f"First item: {data[0] if isinstance(data, list) and data else 'N/A'}")
```

#### 4. 使用结构化日志

```python
LogService.log(
    db,
    level="error",
    category="external_api",
    message="API 调用失败",
    context={
        "platform": "Sorftime",
        "endpoint": "CategoryRequest",
        "error_code": response.code,
        "error_message": response.message,
        "request_params": {...},
        "raw_response": response.text[:1000]  # 关键！
    }
)
```

### 对于运维人员

#### 1. 定期检查日志
- 每日查看 error 日志数量
- 关注 API Quota 消耗趋势
- 监控响应时间异常

#### 2. 设置告警
- API 失败率超过阈值
- Quota 剩余不足
- 响应时间过长

#### 3. 日志清理
- 定期归档旧日志
- 保留关键错误日志
- 清理冗余调试日志

## 常见问题速查表

| 症状 | 可能原因 | 快速检查 |
|------|---------|---------|
| 所有 response 字段为 null | 模型字段映射错误 | 查看原始响应，对比模型定义 |
| code != 0 | API 参数错误或业务异常 | 查看 response.message |
| status_code = 401 | API Key 无效 | 检查配置文件 |
| status_code = 429 | 请求频率超限 | 检查重试策略和延迟 |
| 数据为空但 code=0 | 字段名不匹配或确实无数据 | 打印 data.keys() |
| 超时 | 网络问题或 API 响应慢 | 检查 duration_ms，增加 timeout |

## 工具和脚本

### 1. 快速查询最近错误

```bash
# 在后端容器内
docker exec askjeff-dev-backend-1 python -c "
from app.db.session import SessionLocal
from app.models.log import SystemLog
from sqlalchemy import desc

db = SessionLocal()
logs = db.query(SystemLog).filter(
    SystemLog.level == 'error',
    SystemLog.category == 'external_api'
).order_by(desc(SystemLog.timestamp)).limit(5).all()

for log in logs:
    print(f'{log.timestamp} - {log.message}')
    print(f'  Context: {log.context}')
"
```

### 2. 统计 API 调用情况

```sql
-- 在数据库中执行
SELECT 
    DATE(timestamp) as date,
    level,
    COUNT(*) as count
FROM system_logs
WHERE category = 'external_api'
GROUP BY DATE(timestamp), level
ORDER BY date DESC;
```

## 总结

**记住：日志是排查问题的第一手资料**

1. ✅ 完善的日志 = 快速定位问题
2. ✅ 结构化日志 = 易于分析和统计
3. ✅ 标准流程 = 高效协作
4. ✅ 持续改进 = 减少重复问题

**下次遇到问题时，先看日志！**
