# 008 功能开发总结

## 功能概述

实现了基于 Sorftime API 的批量数据导入功能，用户可以通过输入类目 ID 自动获取 Best Sellers 数据。

**测试阶段限制**：只抓取一批数据（10个产品）

## 已完成的工作

### 1. 核心服务 ✅

创建了 `APIImportService` (`backend/app/services/api_import_service.py`)：

- ✅ 输入解析（支持类目 ID）
- ✅ 获取 Best Sellers Top 100
- ✅ 批量获取产品详情（测试模式：只取前 10 个）
- ✅ 数据入库（ImportBatch + ProductRecord）
- ✅ 生成 Excel 文件
- ✅ 错误处理和日志记录

**测试模式配置**：

```python
self.test_mode = True
self.test_batch_size = 10
```

### 2. API 端点 ✅

在 `backend/app/api/routes/imports.py` 中添加：

- `POST /api/imports/from-api` - 启动 API 导入
- `GET /api/imports/from-api/{batch_id}/status` - 查询导入状态

### 3. 数据库迁移 ✅

添加字段到 `import_batches` 表：

- `source_type VARCHAR(20)` - 导入来源类型（file, api）
- `import_metadata JSONB` - API 导入元数据

### 4. 配置更新 ✅

在 `backend/app/config.py` 中添加：

```python
self.sorftime_api_key = os.getenv("SORFTIME_API_KEY", "")
```

### 5. 测试文件 ✅

创建了测试脚本：

- `backend/test_api_import.py` - 完整功能测试
- `backend/test_api_import_basic.py` - 基本功能测试
- `backend/tests/test_api_import_service.py` - 单元测试

## 核心流程

```
用户输入类目 ID
    ↓
解析输入
    ↓
调用 CategoryRequest API → 获取 Best Sellers Top 100
    ↓
测试模式：只取前 10 个产品
    ↓
分批次调用 ProductRequest API (每批 10 个)
    ↓
数据入库 (ImportBatch + ProductRecord)
    ↓
生成 Excel 文件
    ↓
完成
```

## API 使用示例

### 启动导入

```bash
curl -X POST http://localhost:8001/api/imports/from-api \
  -H "Content-Type: application/json" \
  -d '{
    "input": "172282",
    "input_type": "category_id",
    "domain": 1
  }'
```

响应：

```json
{
  "batch_id": "uuid",
  "status": "started",
  "message": "导入已启动"
}
```

### 查询状态

```bash
curl http://localhost:8001/api/imports/from-api/{batch_id}/status
```

响应：

```json
{
  "batch_id": "uuid",
  "status": "succeeded",
  "total_rows": 10,
  "success_rows": 10,
  "failed_rows": 0,
  "import_metadata": {
    "input_type": "category_id",
    "input_value": "172282",
    "category_id": "172282",
    "domain": 1,
    "start_time": "2025-12-17T10:00:00Z",
    "test_mode": true
  }
}
```

## 测试说明

### 前置条件

1. 确保 Docker 环境运行：

   ```bash
   docker ps
   ```

2. 设置 Sorftime API Key：

   ```bash
   # 在 .env 文件中添加
   SORFTIME_API_KEY=your_api_key_here
   ```

3. 重启后端服务：

   ```bash
   docker restart askjeff-dev-backend-1
   ```

### 运行测试

**注意**：由于测试模式限制，只会抓取 10 个产品，不会抓取完整的 Top 100。

```bash
# 方式 1: 通过 API 测试
curl -X POST http://localhost:8001/api/imports/from-api \
  -H "Content-Type: application/json" \
  -d '{"input": "172282"}'

# 方式 2: 运行测试脚本（需要在容器内）
docker exec askjeff-dev-backend-1 python test_api_import.py
```

## 文件清单

### 新增文件

1. `backend/app/services/api_import_service.py` - API 导入服务
2. `backend/migrations/008_add_api_import_fields.py` - 数据库迁移
3. `backend/test_api_import.py` - 功能测试脚本
4. `backend/test_api_import_basic.py` - 基本测试脚本
5. `backend/tests/test_api_import_service.py` - 单元测试

### 修改文件

1. `backend/app/models/import_batch.py` - 添加 source_type 和 import_metadata 字段
2. `backend/app/services/import_repository.py` - 更新 create_batch 方法
3. `backend/app/api/routes/imports.py` - 添加 API 导入端点
4. `backend/app/config.py` - 添加 Sorftime API Key 配置

## 当前限制

### 测试阶段限制

- ✅ **只抓取 10 个产品**（`test_mode = True`, `test_batch_size = 10`）
- ✅ 不抓取完整的 Top 100
- ✅ **Mock 数据支持**：如果未配置 `SORFTIME_API_KEY`，会自动使用 Mock 数据进行测试

### 功能限制

- ✅ **支持类目 ID 输入**
- ✅ **支持 ASIN 输入** (自动反查类目)
- ✅ **支持 URL 输入** (自动提取 ASIN 或类目 ID)
- ✅ **全量抓取** (可通过 `test_mode=False` 关闭测试模式)

## 下一步计划

### 完整功能开发

1. **移除测试限制**：
   - 设置 `test_mode = False`
   - 抓取完整的 Top 100 产品

2. **扩展输入支持**：
   - 支持 ASIN 输入
   - 支持 URL 解析

3. **前端集成**：
   - 创建 API 导入页面
   - 实时进度展示
   - WebSocket 集成

4. **性能优化**：
   - 优化批次大小
   - 添加缓存机制
   - 失败重试策略

## 技术要点

### 批量处理策略

```python
# 每批 10 个 ASIN
batch_size = 10
batches = [asins[i:i+batch_size] for i in range(0, len(asins), batch_size)]

for i, batch in enumerate(batches):
    # 调用 API
    asin_str = ",".join(batch)
    response = await client.product_request(asin=asin_str, domain=1)
    
    # 延迟（避免限流）
    if i < len(batches) - 1:
        await asyncio.sleep(1)
```

### Excel 生成

```python
import pandas as pd

df = pd.DataFrame(data)
df.to_excel(filepath, index=False, engine="openpyxl")
```

## 注意事项

1. **API Key 配置**：确保 `SORFTIME_API_KEY` 环境变量已设置
2. **测试模式**：当前只抓取 10 个产品，适合测试
3. **数据库字段**：使用 `import_metadata` 而非 `metadata`（避免 SQLAlchemy 保留字冲突）
4. **错误处理**：所有异常都会记录到日志并更新批次状态

## 成功标准

- ✅ 支持类目 ID 输入
- ✅ 成功获取 Best Sellers（测试模式：10 个）
- ✅ 批量获取产品详情
- ✅ 数据正确入库
- ✅ Excel 文件格式正确
- ✅ 错误处理完善
- ✅ 日志记录完整

---

**文档版本**: 1.0  
**最后更新**: 2025-12-17  
**状态**: 测试阶段完成，待完整功能开发
