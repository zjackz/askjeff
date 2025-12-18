# AI 日志分析与问题诊断规范（模板）

> 建议放置位置：项目根目录 `AGENTS/`（便于跨项目复制）。

## 核心原则

### 🔍 问题诊断优先级：日志 > 猜测

当遇到任何 API 调用失败、数据异常或功能错误时，AI 必须：
1. **第一步：查询日志** - 不要盲目修改代码
2. **第二步：分析数据** - 基于实际数据定位问题
3. **第三步：精准修复** - 针对性解决问题
4. **第四步：验证结果** - 修复后再次检查日志

## 日志系统架构

### 配置说明

- **存储位置**: PostgreSQL `system_logs` 表
- **日志分类**:
  - `external_api` - 外部 API 调用（Sorftime, DeepSeek 等）
  - `api_import` - 批量导入业务日志
  - `system` - 系统级日志
- **关键字段**:
  - `level` - 日志级别 (info/error/warning)
  - `category` - 日志分类
  - `message` - 日志消息
  - `context` - JSON 格式的上下文数据
  - `timestamp` - 时间戳

## AI 必须遵循的工作流程

### 场景 1：API 调用失败

**用户报告**: "抓取失败，提示：未获取到数据"

**AI 标准流程**:

```bash
# 1. 查询最近的 API 错误日志
<项目特定的日志查询命令>

# 2. 如果发现响应解析失败，查看原始响应
<查看原始响应的命令>

# 3. 分析数据，定位问题（如：字段名大小写不匹配）
# 4. 修复代码
# 5. 验证修复：再次查询日志确认 level 变为 info
```

### 场景 2：数据解析异常

**症状**: API 返回 200，但所有 response 字段都是 null

**诊断步骤**:
1. 查询 `raw_response` 查看实际返回的 JSON
2. 对比 Pydantic 模型定义
3. 检查字段名映射（如 `RequestLeft` vs `requestLeft`）
4. 修复模型配置或添加 `AliasChoices`

### 场景 3：性能问题

**查询响应时间分布**:

```sql
-- 项目占位符：根据实际日志表结构调整
SELECT 
    context->>'platform' as platform,
    COUNT(*) as calls,
    ROUND(AVG((context->>'duration_ms')::numeric), 0) as avg_ms,
    MAX((context->>'duration_ms')::numeric) as max_ms
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY context->>'platform';
```

## 常用 SQL 查询模板（项目占位符）

### 1. 快速诊断最近错误

```sql
SELECT 
    to_char(timestamp, 'YYYY-MM-DD HH24:MI:SS') as time,
    message,
    context->>'platform' as platform,
    context->'error_detail' as error,
    LEFT(context->>'raw_response', 200) as response_preview
FROM system_logs
WHERE category = 'external_api'
  AND level = 'error'
  AND timestamp >= NOW() - INTERVAL '30 minutes'
ORDER BY timestamp DESC
LIMIT 5;
```

### 2. 检查特定平台的调用

```sql
SELECT 
    to_char(timestamp, 'HH24:MI:SS') as time,
    level,
    context->>'status_code' as status,
    context->'response'->>'code' as api_code
FROM system_logs
WHERE category = 'external_api'
  AND context->>'platform' = '<平台名>'
  AND timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 10;
```

### 3. 统计成功率

```sql
SELECT 
    level,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as percentage
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY level;
```

## 数据库连接信息

### 数据库连接配置

- **容器名**: `askjeff-dev-db-1`
- **用户名**: `sorftime`
- **数据库**: `askjeff`
- **查询命令格式**:

  ```bash
  docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c "<SQL>"
  ```

## 最佳实践

**对于 AI**:
- ✅ **问题出现时，第一反应是查日志**
- ✅ **使用精确的时间范围**（用户刚报告的问题查最近 10-30 分钟）
- ✅ **逐步深入**：先看概览统计，再看详情，最后看原始数据
- ✅ **修复后必须验证**：重新查询日志确认问题解决
- ❌ **不要盲目猜测和修改代码**

**对于开发者**:
- ✅ **完善日志记录**：关键节点都要记录，错误时记录完整上下文
- ✅ **使用结构化数据**：context 字段使用 JSON 格式
- ✅ **失败时记录原始响应**：便于调试解析问题

## 日志记录规范

**在代码中记录日志**:

```python
# 成功的 API 调用
LogService.log(
    db,
    level="info",
    category="external_api",
    message="API Request Success",
    context={
        "platform": "ExternalService",
        "url": str(response.url),
        "status_code": response.status_code,
        "duration_ms": duration,
        "response": {
            "code": response_data.get("code"),
            "key_field": response_data.get("key_field")
        }
    }
)

# 失败的 API 调用（额外记录 raw_response）
LogService.log(
    db,
    level="error",
    category="external_api",
    message="API Request Failed",
    context={
        "platform": "ExternalService",
        "url": str(response.url),
        "status_code": response.status_code,
        "raw_response": response.text[:2000],  # 关键！
        "error_detail": {
            "http_status": response.status_code,
            "api_code": response_data.get("code"),
            "api_message": response_data.get("message")
        }
    }
)
```

## 工作流程文档

### 相关工作流程

详细的日志分析流程和诊断方法，参见：
- `.agent/workflows/ai-log-analysis.md` - AI 专用诊断指南
- `.agent/workflows/troubleshoot-api-issues.md` - 用户/开发者手册
