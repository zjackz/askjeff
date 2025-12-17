# 需求 008: API 批量导入功能

**需求编号**: 008  
**需求名称**: API Batch Import  
**优先级**: 高  
**预估工时**: 12 小时  
**创建日期**: 2025-12-17  
**状态**: 已完成 (前端已集成)

---

## 1. 概述

实现基于 Sorftime API 的批量数据导入功能，用户通过输入 ASIN 或链接即可自动获取 Best Sellers Top 100 数据，分批次调用详情 API，数据入库并生成 Excel，最后对接现有的导入流程完成后续处理。

---

## 2. 背景与目标

### 背景

当前系统已实现：
- ✅ Sorftime API 集成（需求 005）
- ✅ CSV/Excel 导入功能
- ✅ 数据清洗和提取流程

### 痛点

- 用户需要手动下载数据再上传
- 无法直接从 API 批量获取数据
- 缺少自动化的数据采集流程

### 目标

1. **简化流程**: 输入 ASIN/链接 → 自动获取 Top 100 → 入库
2. **批量处理**: 分批次调用 API，避免超时和限流
3. **无缝对接**: 复用现有的导入、清洗、提取流程
4. **用户友好**: 实时进度反馈，生成 Excel 供下载

---

## 3. 功能需求

### 3.1 输入方式

支持以下输入：

| 输入类型 | 示例 | 说明 |
|---------|------|------|
| **ASIN** | B08N5WRWNW | 单个产品 ASIN |
| **类目 ID** | 172282 | Amazon Node ID |
| **产品链接** | <https://www.amazon.com/dp/B08N5WRWNW> | 产品详情页 |
| **类目链接** | <https://www.amazon.com/s?node=172282> | 类目页面 |

### 3.2 核心流程

```
用户输入 (ASIN/链接)
    ↓
解析输入 → 获取类目 ID
    ↓
调用 CategoryRequest API → 获取 Best Sellers Top 100
    ↓
分批次调用 ProductRequest API (每批 10 个)
    ↓
数据入库 (ImportBatch + ProductRecord)
    ↓
生成 Excel 文件
    ↓
对接现有导入流程 (清洗 + 提取)
    ↓
完成
```

### 3.3 API 调用策略

#### 第 1 步：获取 Best Sellers

**API**: `CategoryRequest`

```python
response = await sorftime.category_request(
    node_id="172282",
    domain=1
)
# 返回: Top 100 产品的基础信息
```

#### 第 2 步：批量获取详情

**API**: `ProductRequest`

**批次策略**:
- 每批 10 个 ASIN
- 批次间延迟 1 秒（避免限流）
- 失败重试 3 次

```python
# 示例
asins = ["B001", "B002", ..., "B100"]  # 100 个
batches = [asins[i:i+10] for i in range(0, 100, 10)]  # 10 批

for batch in batches:
    asin_str = ','.join(batch)
    response = await sorftime.product_request(
        asin=asin_str,
        trend=0,  # 不需要趋势数据
        domain=1
    )
    await asyncio.sleep(1)  # 延迟
```

### 3.4 数据存储

#### ImportBatch 记录

```python
{
    "id": "uuid",
    "filename": "api_import_172282_20251217.xlsx",
    "source_type": "api",  # 新增类型
    "status": "processing",
    "total_rows": 100,
    "processed_rows": 0,
    "metadata": {
        "input_type": "category_id",
        "input_value": "172282",
        "category_name": "Electronics",
        "api_calls": 11,  # 1 + 10 批次
        "start_time": "2025-12-17T10:00:00Z"
    }
}
```

#### ProductRecord 记录

```python
{
    "batch_id": "uuid",
    "asin": "B08N5WRWNW",
    "title": "Echo Dot (4th Gen)",
    "price": 49.99,
    "ratings": 4.7,
    "reviews_count": 50000,
    "raw_data": {...},  # 完整 API 响应
    "status": "pending"
}
```

### 3.5 Excel 生成

**格式**: 与现有导入格式一致

| 列名 | 说明 | 示例 |
|------|------|------|
| ASIN | 产品 ASIN | B08N5WRWNW |
| Title | 产品标题 | Echo Dot (4th Gen) |
| Price | 价格 | 49.99 |
| Rating | 评分 | 4.7 |
| Reviews | 评论数 | 50000 |
| Category | 类目 | Electronics |
| ... | 其他字段 | ... |

**存储位置**: `uploads/api_imports/`

### 3.6 进度反馈

**WebSocket 实时推送**:

```json
{
    "type": "progress",
    "batch_id": "uuid",
    "stage": "fetching_details",
    "progress": 45,
    "message": "正在获取产品详情 (45/100)",
    "current_batch": 5,
    "total_batches": 10
}
```

**阶段**:
1. `parsing_input` - 解析输入
2. `fetching_bestsellers` - 获取 Best Sellers
3. `fetching_details` - 批量获取详情
4. `saving_data` - 保存数据
5. `generating_excel` - 生成 Excel
6. `processing` - 对接导入流程
7. `completed` - 完成

---

## 4. 技术设计

### 4.1 后端架构

#### 新增服务

```python
# backend/app/services/api_import_service.py

class APIImportService:
    """API 批量导入服务"""
    
    async def import_from_input(
        self,
        input_value: str,
        input_type: str,  # asin, category_id, url
        domain: int = 1
    ) -> str:
        """
        从输入启动导入流程
        
        Returns:
            batch_id: 导入批次 ID
        """
        pass
    
    async def _parse_input(self, input_value: str) -> dict:
        """解析输入，识别类型和提取信息"""
        pass
    
    async def _fetch_bestsellers(self, category_id: str, domain: int) -> list:
        """获取 Best Sellers Top 100"""
        pass
    
    async def _fetch_details_batch(self, asins: list, domain: int) -> list:
        """批量获取产品详情"""
        pass
    
    async def _save_to_database(self, batch_id: str, products: list):
        """保存到数据库"""
        pass
    
    async def _generate_excel(self, batch_id: str) -> str:
        """生成 Excel 文件"""
        pass
    
    async def _trigger_import_flow(self, batch_id: str):
        """触发现有导入流程"""
        pass
```

#### API 端点

```python
# POST /api/v1/imports/from-api
{
    "input": "172282",  # 或 ASIN, URL
    "input_type": "category_id",  # 可选，自动识别
    "domain": 1
}

# Response
{
    "batch_id": "uuid",
    "status": "started",
    "estimated_time": 120  # 秒
}

# GET /api/v1/imports/from-api/{batch_id}/status
{
    "batch_id": "uuid",
    "status": "processing",
    "progress": 45,
    "stage": "fetching_details",
    "message": "正在获取产品详情 (45/100)"
}
```

### 4.2 前端设计

#### 新增页面

**路由**: `/imports/api`

**UI 组件**:

```
┌─────────────────────────────────────────┐
│  📥 API 批量导入                         │
├─────────────────────────────────────────┤
│  输入 ASIN、类目 ID 或链接:              │
│  ┌─────────────────────────────────┐    │
│  │ 172282                          │    │
│  └─────────────────────────────────┘    │
│  站点: [美国 ▼]                         │
│  [🚀 开始导入]                          │
├─────────────────────────────────────────┤
│  📊 导入进度                             │
│  ┌───────────────────────────────────┐  │
│  │  ✅ 解析输入                       │  │
│  │  ✅ 获取 Best Sellers (100 个)    │  │
│  │  🔄 获取产品详情 (45/100)         │  │
│  │  ░░░░░░░░░░░░░░░░░░░░ 45%        │  │
│  │  ⏳ 保存数据                       │  │
│  │  ⏳ 生成 Excel                     │  │
│  │  ⏳ 对接导入流程                   │  │
│  └───────────────────────────────────┘  │
│  预计剩余时间: 1 分 30 秒                │
└─────────────────────────────────────────┘
```

#### 功能特性

1. **智能识别**: 自动识别输入类型
2. **实时进度**: WebSocket 推送进度
3. **错误提示**: 友好的错误信息
4. **结果展示**: 完成后跳转到导入列表

---

## 5. 实施计划

### 阶段 1: 后端核心功能 (6h)

**Task 1.1**: 创建 APIImportService (2h)
- 实现输入解析
- 实现 Best Sellers 获取
- 实现批量详情获取

**Task 1.2**: 数据存储和 Excel 生成 (2h)
- 保存到 ImportBatch 和 ProductRecord
- 生成 Excel 文件
- 对接现有导入流程

**Task 1.3**: API 端点 (2h)
- POST /api/v1/imports/from-api
- GET /api/v1/imports/from-api/{id}/status
- WebSocket 进度推送

### 阶段 2: 前端实现 (4h)

**Task 2.1**: API 导入页面 (3h)
- 输入表单
- 进度展示
- WebSocket 集成

**Task 2.2**: 路由和导航 (1h)
- 添加路由
- 更新导航菜单

### 阶段 3: 测试和优化 (2h)

**Task 3.1**: 功能测试 (1h)
- 测试各种输入类型
- 测试批量处理
- 测试错误场景

**Task 3.2**: 性能优化 (1h)
- 优化批次大小
- 优化延迟时间
- 添加缓存

---

## 6. 技术要点

### 6.1 输入解析

```python
def parse_input(input_value: str) -> dict:
    """
    解析输入，识别类型
    
    Returns:
        {
            "type": "category_id" | "asin" | "url",
            "value": "172282",
            "domain": 1
        }
    """
    # ASIN: B + 9 位字母数字
    if re.match(r'^B[A-Z0-9]{9}$', input_value):
        return {"type": "asin", "value": input_value}
    
    # 类目 ID: 纯数字
    if input_value.isdigit():
        return {"type": "category_id", "value": input_value}
    
    # URL: 提取 ASIN 或 Node ID
    if 'amazon.com' in input_value:
        # 提取逻辑
        pass
    
    raise ValueError("无法识别的输入格式")
```

### 6.2 批量处理

```python
async def fetch_details_in_batches(asins: list, batch_size: int = 10):
    """分批次获取详情"""
    results = []
    batches = [asins[i:i+batch_size] for i in range(0, len(asins), batch_size)]
    
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i+1}/{len(batches)}")
        
        # 调用 API
        asin_str = ','.join(batch)
        response = await sorftime.product_request(asin=asin_str, domain=1)
        
        if response.code == 0:
            results.extend(response.data)
        
        # 进度推送
        await push_progress(batch_id, i+1, len(batches))
        
        # 延迟（避免限流）
        if i < len(batches) - 1:
            await asyncio.sleep(1)
    
    return results
```

### 6.3 Excel 生成

```python
import pandas as pd

def generate_excel(products: list, filename: str):
    """生成 Excel 文件"""
    df = pd.DataFrame([{
        'ASIN': p.get('asin'),
        'Title': p.get('title'),
        'Price': p.get('price'),
        'Rating': p.get('ratings'),
        'Reviews': p.get('ratingsCount'),
        # ... 其他字段
    } for p in products])
    
    filepath = f"uploads/api_imports/{filename}"
    df.to_excel(filepath, index=False)
    
    return filepath
```

---

## 7. 成功标准

- ✅ 支持 ASIN、类目 ID、URL 输入
- ✅ 成功获取 Best Sellers Top 100
- ✅ 批量获取产品详情（成功率 > 95%）
- ✅ 数据正确入库
- ✅ Excel 文件格式正确
- ✅ 对接现有导入流程无缝
- ✅ 实时进度反馈
- ✅ 错误处理完善

---

## 8. 风险和限制

### 风险

1. **API 限流**: Sorftime API 可能有调用频率限制
   - 缓解：批次间延迟，失败重试

2. **数据量大**: Top 100 可能需要较长时间
   - 缓解：异步处理，进度反馈

3. **网络超时**: API 调用可能超时
   - 缓解：设置合理超时，重试机制

### 限制

- 单次最多导入 100 个产品
- 需要有效的 Sorftime API Key
- 依赖 Sorftime API 稳定性

---

## 9. 后续扩展

1. **支持自定义数量**: 不限于 Top 100
2. **支持多类目**: 一次导入多个类目
3. **定时任务**: 定期自动更新数据
4. **数据对比**: 与历史数据对比变化

---

**文档版本**: 1.0  
**最后更新**: 2025-12-17  
**作者**: AI Assistant  
**状态**: 规格说明完成，待实施
