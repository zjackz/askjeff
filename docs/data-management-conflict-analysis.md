# 数据管理模块冲突分析

## 📊 现有数据管理模块

### 1. 文件导入模块
**职责**: 从文件导入数据

**表结构**:
- `import_batches` - 导入批次
- `product_records` - 产品记录

**服务**:
- `ImportService` - CSV/XLSX 文件导入
- `APIImportService` - Sorftime API 批量导入

**数据来源**:
- Sorftime API (第三方数据）
- 用户上传的 CSV/XLSX 文件

---

### 2. Amazon 数据同步模块 (新)
**职责**: 从 Amazon API 同步真实业务数据

**表结构**:
- `amazon_stores` - Amazon 店铺
- `inventory_snapshots` - 库存快照
- `business_metric_snapshots` - 业务指标快照
- `ads_metric_snapshots` - 广告指标快照
- `sync_tasks` - 同步任务记录

**服务**:
- `AmazonSyncService` - Amazon 数据同步
- `DataEngineService` - Jeff Data Core 桥接

**数据来源**:
- Amazon SP-API (库存/业务报告）
- Amazon Advertising API (广告数据）

---

### 3. Jeff Data Core (JDC)
**职责**: 独立的数据引擎，处理外部 API 集成

**表结构**:
- `jdc_raw_data_logs` - 原始数据日志（JSONB）

**组件**:
- `AmazonAdsConnector` - Amazon Ads API
- `PostgresStorage` - PostgreSQL 存储
- `JeffDataEngine` - 数据编排引擎

---

## ⚠️ 潜在冲突分析

### 1. 功能重叠

| 功能 | 文件导入 | Amazon 同步 | 冲突风险 |
|------|---------|------------|---------|
| 数据来源 | Sorftime API / 文件 | Amazon API | ❌ 低 |
| 数据类型 | 产品信息（市场数据） | 真实业务数据 | ❌ 无 |
| 数据用途 | 产品分析、选品 | 广告诊断、运营分析 | ❌ 无 |
| 数据刷新 | 手动导入 | 自动同步 | ❌ 无 |

**结论**: 无功能重叠，用途互补

---

### 2. 数据表冲突

#### ProductRecord vs Amazon 数据表

```sql
-- ProductRecord (文件导入)
product_records (
    id,              -- UUID
    asin,            -- 产品 ASIN
    title,            -- 产品标题
    category,         -- 分类
    price,            -- 价格
    data_source,      -- 'file' | 'api'
    ...
)

-- Amazon 快照表 (Amazon 同步)
inventory_snapshots (
    id,              -- UUID
    store_id,         -- 店铺 ID (Amazon)
    asin,            -- 产品 ASIN
    fba_inventory,    -- FBA 库存
    date,             -- 日期
    ...
)

business_metric_snapshots (
    id,              -- UUID
    store_id,         -- 店铺 ID (Amazon)
    asin,            -- 产品 ASIN
    total_sales_amount, -- 销售额
    total_units_ordered, -- 销量
    date,             -- 日期
    ...
)

ads_metric_snapshots (
    id,              -- UUID
    store_id,         -- 店铺 ID (Amazon)
    asin,            -- 产品 ASIN
    spend,            -- 广告花费
    sales,            -- 广告销售
    date,             -- 日期
    ...
)
```

**潜在问题**:
- ❌ ASIN 字段存在多个表中
- ❌ 产品数据分散在不同位置
- ❌ 难以统一查询和分析

---

### 3. 用户界面重叠

#### 现有页面
- `/import` - 文件导入
- `/product` - 产品列表（来自文件导入）
- `/export` - 数据导出
- `/admin` - 数据管理（清空数据）

#### 新增页面
- `/data-source` - 数据源管理（新）

**重叠点**:
- ❌ `/product` 显示 `ProductRecord` 数据
- ❌ `/data-source` 配置 Amazon 店铺
- ⚠️ 用户可能困惑：产品数据从哪里来？

---

## ✅ 建议的解决方案

### 方案 1: 明确用途分离（推荐）

**策略**: 保持两个模块独立，明确各自用途

#### 文件导入模块
**用途**: 市场调研、竞品分析
**数据来源**: Sorftime API（第三方数据）
**使用场景**:
- 选品分析
- 市场趋势研究
- 竞品对比

#### Amazon 同步模块
**用途**: 业务运营、广告优化
**数据来源**: Amazon API（真实业务数据）
**使用场景**:
- 广告诊断
- 库存管理
- 运营分析

**界面说明**:
- `/import` - 标注："导入市场数据（Sorftime）"
- `/data-source` - 标注："配置真实业务数据源（Amazon）"
- `/product` - 提供数据来源切换

---

### 方案 2: 统一产品数据模型（长期）

**策略**: 将 Amazon 数据映射到 ProductRecord

#### 新增字段
```python
# 扩展 ProductRecord
class ProductRecord(Base):
    # ... 现有字段

    # Amazon 数据关联
    store_id: Mapped[UUID] = mapped_column(...)  # 关联 amazon_stores
    sync_type: Mapped[str] = mapped_column(...)   # 'file', 'api', 'amazon'

    # Amazon 特定字段
    fba_inventory: Mapped[int] = mapped_column(...)
    ad_spend: Mapped[float] = mapped_column(...)
    ad_sales: Mapped[float] = mapped_column(...)
```

#### 优势
- ✅ 产品数据统一在一张表
- ✅ 统一的查询和分析
- ✅ 简化前端逻辑

#### 劣势
- ❌ 需要大规模重构
- ❌ Amazon 时间序列数据结构复杂
- ❌ 不利于时间序列分析

---

### 方案 3: 保持分离，提供联动（折中）

**策略**: 两个模块独立，但提供数据关联

#### 关联方式
```python
# ProductRecord 中关联 Amazon 数据
class ProductRecord(Base):
    asin: Mapped[str] = mapped_column(...)
    amazon_asin: Mapped[Optional[str]] = mapped_column(...)  # 关联 Amazon ASIN
```

#### 前端显示
```
产品详情页：
- 市场数据 (Sorftime)    来自 ProductRecord
- 业务数据 (Amazon)      来自 Amazon 快照表
- 对比分析              联合查询
```

#### 优势
- ✅ 保持现有架构
- ✅ 提供数据联动
- ✅ 不需要大规模重构

#### 劣势
- ❌ 需要复杂的 JOIN 查询
- ❌ 数据一致性难以保证

---

## 🎯 推荐方案

### 短期（1-2 周）
**采用方案 1**: 明确用途分离

**行动**:
1. 在 `/import` 页面添加说明
   - "导入市场数据（来自 Sorftime）"

2. 在 `/data-source` 页面添加说明
   - "配置真实业务数据源（来自 Amazon）"

3. 在 `/product` 页面添加数据来源筛选
   - "全部数据"
   - "市场数据（Sorftime）"
   - "业务数据（Amazon）"

**优势**:
- ✅ 无需重构
- ✅ 快速实施
- ✅ 用户界面清晰

---

### 长期（1-2 个月）
**采用方案 2**: 统一产品数据模型

**行动**:
1. 设计统一的产品数据模型
2. 迁移 Amazon 数据到新结构
3. 重构前端查询逻辑
4. 编写数据迁移脚本

**优势**:
- ✅ 数据架构统一
- ✅ 便于维护
- ✅ 便于扩展

---

## 📋 冲突风险评估

| 风险 | 严重程度 | 概率 | 缓解措施 |
|------|---------|------|---------|
| 用户界面混淆 | 中 | 高 | 清晰的页面说明、数据来源标识 |
| 数据分散导致查询困难 | 中 | 中 | 提供 API 端点联合查询 |
| 性能问题（表多） | 低 | 低 | 数据库索引优化 |
| 数据一致性难保证 | 中 | 高 | 数据同步策略、事务管理 |

---

## 💡 最终建议

### 立即行动
1. ✅ **保持现状** - 两个模块独立运行
2. ✅ **添加说明** - 清晰标注各自用途
3. ✅ **页面优化** - 添加数据来源筛选

### 未来优化
1. 📋 **数据整合** - 评估统一模型的必要性
2. 📋 **性能优化** - 监控查询性能
3. 📋 **用户体验** - 收集用户反馈，调整界面

---

## 结论

**当前状态**: 无严重冲突，架构合理

**原因**:
- 两个模块用途不同（市场数据 vs 业务数据）
- 数据表结构不同（静态 vs 时间序列）
- API 端点独立

**建议**: 采用方案 1（明确分离），长期评估统一
