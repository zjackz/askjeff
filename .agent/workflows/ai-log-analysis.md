---
description: AI 自动化日志分析和问题诊断的标准工作流程
---

# AI 日志分析工作流程

## 核心理念

**当遇到任何 API 或系统问题时，AI 应该：**
1. 🔍 **先查日志** - 不要盲目猜测
2. 📊 **自动分析** - 使用工具快速诊断
3. 💡 **精准修复** - 基于数据做决策
4. ✅ **验证结果** - 修复后再次检查日志

## 工作流程

### Step 1: 识别问题场景

**触发条件：**
- 用户报告错误（如："未获取到 Best Sellers 数据"）
- 功能测试失败
- 性能异常
- 数据不一致

**AI 应该立即想到：** "这个问题可能在日志中有记录"

### Step 2: 查询相关日志

#### 方法 A：使用 SQL 直接查询（推荐）

```sql
-- 查询最近的 API 错误
SELECT 
    timestamp,
    message,
    context->>'platform' as platform,
    context->>'url' as url,
    context->>'status_code' as status,
    context->'response'->>'code' as api_code,
    context->'response'->>'message' as api_message,
    context->>'raw_response' as raw_response
FROM system_logs
WHERE category = 'external_api'
  AND level = 'error'
  AND timestamp >= NOW() - INTERVAL '30 minutes'
ORDER BY timestamp DESC
LIMIT 10;
```

**执行命令：**

```bash
docker exec askjeff-dev-db-1 psql -U <用户名> -d askjeff -c "<SQL>"
```

#### 方法 B：查询特定平台的调用

```sql
-- 查询 Sorftime API 的最近调用
SELECT 
    to_char(timestamp, 'HH24:MI:SS') as time,
    level,
    message,
    context->>'status_code' as status,
    context->'response'->>'code' as api_code,
    context->'response'->>'requestLeft' as quota
FROM system_logs
WHERE category = 'external_api'
  AND context->>'platform' = 'Sorftime'
  AND timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

#### 方法 C：统计分析

```sql
-- 统计最近的 API 调用情况
SELECT 
    context->>'platform' as platform,
    level,
    COUNT(*) as count,
    ROUND(AVG((context->>'duration_ms')::numeric), 0) as avg_ms
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY context->>'platform', level
ORDER BY count DESC;
```

### Step 3: 分析日志数据

**关键检查点：**

1. **HTTP 状态码**
   - `200` = 请求成功，继续检查业务状态
   - `4xx` = 客户端错误（参数、权限）
   - `5xx` = 服务器错误

2. **API 业务状态码** (`response.code`)
   - `0` = 成功
   - `非0` = 业务错误，查看 `response.message`

3. **响应解析**
   - 如果 `response` 所有字段都是 `null` → 模型解析失败
   - 查看 `raw_response` 了解实际结构

4. **数据结构**
   - 检查字段名大小写（`Products` vs `products`）
   - 检查数据嵌套层级
   - 检查数据类型

### Step 4: 诊断问题类型

#### 类型 1：模型解析失败
**症状：** `response` 字段全是 `null`，但 `status_code=200`

**诊断步骤：**
1. 查询 `raw_response`
2. 对比 Pydantic 模型定义
3. 检查字段映射和 `AliasChoices`

**示例 SQL：**

```sql
SELECT 
    context->>'raw_response' as raw_response
FROM system_logs
WHERE category = 'external_api'
  AND level = 'error'
  AND context->'response'->>'code' IS NULL
ORDER BY timestamp DESC
LIMIT 1;
```

**修复方向：**
- 添加 `model_config = ConfigDict(populate_by_name=True)`
- 更新 `AliasChoices`
- 修改数据提取逻辑

#### 类型 2：API 返回错误
**症状：** `response.code != 0`

**诊断步骤：**
1. 查看 `response.message`
2. 检查 `request` 参数
3. 检查 API 文档

**示例 SQL：**

```sql
SELECT 
    context->'request' as request,
    context->'response'->>'code' as code,
    context->'response'->>'message' as message
FROM system_logs
WHERE category = 'external_api'
  AND (context->'response'->>'code')::int != 0
ORDER BY timestamp DESC
LIMIT 5;
```

#### 类型 3：数据为空
**症状：** `code=0` 但业务逻辑报错"未获取到数据"

**诊断步骤：**
1. 检查应用日志中的调试信息
2. 查看数据提取逻辑
3. 检查字段名匹配

**示例 SQL：**

```sql
-- 查看应用日志中的调试信息
SELECT 
    timestamp,
    message,
    context
FROM system_logs
WHERE category = 'api_import'
  AND message LIKE '%Best Sellers%'
  AND timestamp >= NOW() - INTERVAL '30 minutes'
ORDER BY timestamp DESC;
```

### Step 5: 实施修复

**修复后必须：**
1. 重启相关服务
2. 重新触发操作
3. **再次查询日志验证**

**验证 SQL：**

```sql
-- 检查最新的调用是否成功
SELECT 
    timestamp,
    level,
    message,
    context->'response'->>'code' as api_code
FROM system_logs
WHERE category = 'external_api'
  AND context->>'platform' = 'Sorftime'
ORDER BY timestamp DESC
LIMIT 5;
```

## AI 使用指南

### 场景 1：用户报告 API 错误

```
用户: "抓取失败，提示：未获取到 Best Sellers 数据"

AI 思考过程：
1. 这是 API 调用问题 → 查 external_api 日志
2. 关键词：Best Sellers → 可能是 CategoryRequest
3. 执行 SQL 查询最近的 Sorftime 日志
4. 分析返回数据
5. 定位问题（如：字段解析失败）
6. 修复代码
7. 验证修复
```

**AI 执行命令：**

```bash
# 1. 查询最近的错误
docker exec askjeff-dev-db-1 psql -U <用户> -d askjeff -c "
SELECT timestamp, message, context->'error_detail' as error
FROM system_logs
WHERE category = 'external_api' AND level = 'error'
  AND timestamp >= NOW() - INTERVAL '10 minutes'
ORDER BY timestamp DESC LIMIT 3;
"

# 2. 查看原始响应
docker exec askjeff-dev-db-1 psql -U <用户> -d askjeff -c "
SELECT context->>'raw_response'
FROM system_logs
WHERE category = 'external_api'
  AND message LIKE '%CategoryRequest%'
ORDER BY timestamp DESC LIMIT 1;
"

# 3. 分析并修复
# 4. 验证
```

### 场景 2：性能问题

```
用户: "API 调用很慢"

AI 执行：
```

```sql
-- 查询响应时间分布
SELECT 
    context->>'platform' as platform,
    COUNT(*) as calls,
    MIN((context->>'duration_ms')::numeric) as min_ms,
    AVG((context->>'duration_ms')::numeric) as avg_ms,
    MAX((context->>'duration_ms')::numeric) as max_ms
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY context->>'platform';
```

### 场景 3：Quota 监控

```sql
-- 检查 Quota 使用情况
SELECT 
    timestamp,
    context->'response'->>'requestConsumed' as consumed,
    context->'response'->>'requestLeft' as left
FROM system_logs
WHERE category = 'external_api'
  AND context->>'platform' = 'Sorftime'
  AND context->'response'->>'requestLeft' IS NOT NULL
ORDER BY timestamp DESC
LIMIT 10;
```

## 常用 SQL 查询模板

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

### 2. 检查特定端点

```sql
SELECT 
    timestamp,
    level,
    context->>'status_code' as status,
    context->'response'->>'code' as api_code,
    context->'request' as request
FROM system_logs
WHERE category = 'external_api'
  AND context->>'url' LIKE '%CategoryRequest%'
  AND timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

### 3. 成功率统计

```sql
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) FILTER (WHERE level = 'info') as success,
    COUNT(*) FILTER (WHERE level = 'error') as failed,
    ROUND(100.0 * COUNT(*) FILTER (WHERE level = 'info') / COUNT(*), 1) as success_rate
FROM system_logs
WHERE category = 'external_api'
  AND timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;
```

## 最佳实践

### 对于 AI

1. **问题出现时，第一反应是查日志**
   - 不要直接修改代码
   - 先了解实际发生了什么

2. **使用精确的时间范围**
   - 用户刚报告的问题 → 查最近 10-30 分钟
   - 历史问题 → 根据用户描述调整

3. **逐步深入**
   - 先看概览（统计）
   - 再看详情（具体错误）
   - 最后看原始数据（raw_response）

4. **修复后必须验证**
   - 重新查询日志
   - 确认 level 变为 info
   - 确认数据正确返回

5. **记录诊断过程**
   - 在代码注释或文档中说明
   - 帮助未来的调试

### 对于开发者

1. **完善日志记录**
   - 关键节点都要记录
   - 错误时记录完整上下文
   - 使用结构化数据

2. **定期检查日志**
   - 每日查看错误数量
   - 关注性能趋势
   - 监控 Quota 使用

3. **优化日志查询**
   - 为常用字段添加索引
   - 定期清理旧日志
   - 使用日志聚合工具

## 工具清单

- ✅ SQL 查询模板（本文档）
- ✅ `analyze_api_logs.py`（自动化分析脚本）
- ✅ `quick_check_api_logs.sh`（快速检查脚本）
- ✅ 前端日志监控页面
- ✅ Workflow 文档

## 总结

**核心原则：数据驱动，精准诊断**

- 📊 日志是真相的来源
- 🔍 分析比猜测更高效
- 💡 数据指导决策
- ✅ 验证确保质量

**AI 的工作模式：**

```
问题 → 查日志 → 分析数据 → 定位原因 → 修复代码 → 验证结果
```

**而不是：**

```
问题 → 猜测原因 → 尝试修复 → 失败 → 再猜测 → ...
```
