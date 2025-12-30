# 技术实施计划: 009-amazon-ads-analysis

## 1. 技术栈选择

### 后端 (Backend)

- **框架**: FastAPI (现有架构)
- **数据处理**: Pandas (用于高效处理广告报表和库存数据)
- **数据库**:
  - PostgreSQL (存储业务数据、快照、诊断结果)
  - Redis (缓存实时查询结果)
- **外部接口**:
  - `sp-api` (Amazon Selling Partner API): 获取库存、销量。
  - `amazon-advertising-api`: 获取广告报表。
- **AI 模型**:
  - Google Gemini 2.0 Flash (用于生成自然语言诊断报告)

### 前端 (Frontend)

- **框架**: Vue 3 + Vite
- **UI 组件库**: PrimeVue / TailwindCSS (保持现有风格)
- **图表库**: ECharts (用于展示 ACOS/TACOS 趋势图)
- **数据展示**: Ag-Grid 或 PrimeVue DataTable (用于展示复杂的诊断矩阵)

## 2. 架构设计

### 2.1 数据流架构

```
[Amazon SP-API] --(Daily Sync)--> [Raw Data Store (PG)]
[Amazon Ads API] --(Daily Sync)--> [Raw Data Store (PG)]
       |
       v
[Data Aggregator (Pandas)] --> [Unified Metrics (SKU Level)]
       |
       v
[Diagnosis Engine (Rules)] --> [Diagnosis Result (JSON)]
       |
       v
[AI Advisor (LLM)] --> [Natural Language Report]
```

### 2.2 核心模块设计

#### A. 数据同步服务 (Data Sync Service)

- **任务**: 每日定时任务 (Celery/APScheduler)。
- **逻辑**:
    1. 拉取昨日 FBA 库存报告。
    2. 拉取昨日 业务报告 (Sales & Traffic)。
    3. 拉取昨日 广告报告 (Sponsored Products - Advertised Product Report)。
    4. 数据清洗与入库。

#### B. 诊断引擎 (Diagnosis Engine)

- **输入**: 统一指标数据 (SKU, Stock, Sales, AdSpend, etc.)
- **规则库**:
  - `Stock_Level`: High (>3 months), Healthy (1-3 months), Low (<1 month)
  - `Ad_Performance`: High_ACOS, Low_ACOS
  - `Biz_Performance`: High_TACOS, Low_TACOS
- **输出**: 诊断标签 (e.g., "OVERSTOCK_HIGH_ACOS")

#### C. 建议生成器 (Recommendation Generator)

- **基于规则**:
  - If `OVERSTOCK_HIGH_ACOS` -> Suggest "Aggressive Clearance"
- **基于 AI**:
  - Prompt: "Analyze this SKU data: {json_data}. Inventory is high (10 months). ACOS is 40%. Give strategic advice."

## 3. 数据库设计 (简略)

### `ads_diagnosis_snapshots`

- `id`: UUID
- `date`: Date
- `sku`: String
- `asin`: String
- `inventory_level`: Integer
- `weeks_of_cover`: Float
- `acos`: Float
- `tacos`: Float
- `diagnosis_tag`: String (Enum)
- `ai_suggestion`: Text

## 4. 接口设计 (API Endpoints)

- `GET /api/v1/ads/diagnosis/overview`: 获取整体账户健康度
- `GET /api/v1/ads/diagnosis/matrix`: 获取 SKU 级诊断矩阵 (支持分页/筛选)
- `POST /api/v1/ads/diagnosis/analyze`: 触发实时/手动诊断
- `GET /api/v1/ads/diagnosis/{sku}/detail`: 获取单个 SKU 的详细趋势与建议

## 5. 开发阶段规划

1. **Phase 1 (Data)**: 打通 SP-API 和 Ads API，实现数据落地。
2. **Phase 2 (Logic)**: 实现 Pandas 数据合并与指标计算逻辑。
3. **Phase 3 (UI)**: 开发前端诊断大盘。
4. **Phase 4 (AI)**: 接入 LLM 生成文字报告。
