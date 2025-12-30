# 任务分解清单: 009-amazon-ads-analysis

## Phase 1: 数据基础设施 (Data Infrastructure)

- [x] **Task 1.1: 数据库模型设计**
  - 创建 `ProductCost` 模型 (SKU, COGS, Currency).
  - 创建 `InventorySnapshot` 模型 (SKU, Date, FBA_Qty, Inbound_Qty, Reserved_Qty).
  - 创建 `AdsMetricSnapshot` 模型 (SKU, Date, Spend, Sales, Impressions, Clicks).
  - 创建 `BusinessMetricSnapshot` 模型 (SKU, Date, Total_Sales, Sessions).
  - 编写并运行 Alembic 迁移脚本.

- [x] **Task 1.2: 数据模拟生成器 (Mock Data Generator)**
  - *鉴于 API 接入耗时，先构建 Mock 数据以加速前端开发.*
  - 编写脚本生成 50 个 SKU 的过去 30 天模拟数据.
  - 确保覆盖四象限场景 (积压/缺货/盈利/亏损).

- [x] **Task 1.3: 核心指标计算服务**
  - 实现 `MetricsService` (Implemented in `AdsAnalysisService`).
  - 计算 `Weeks of Cover` (库存周转周数).
  - 计算 `TACOS` (Total Advertising Cost of Sales).
  - 计算 `Net Margin` (净利率, 需结合 COGS).

## Phase 2: 诊断引擎 (Diagnosis Engine)

- [x] **Task 2.1: 象限分类逻辑**
  - 实现 `DiagnosisService.classify_sku(sku_metrics)` (Implemented in `AdsAnalysisService`).
  - 逻辑:
    - **Q1 (急救)**: Stock > 180 days & TACOS > Margin.
    - **Q2 (明星)**: Stock 30-90 days & TACOS < 10%.
    - **Q3 (潜力)**: Stock < 14 days & Sales Trend > 0.
    - **Q4 (鸡肋)**: Low Sales & Low Stock.
  - 输出: `QuadrantEnum`, `ActionTag` (e.g., "CLEARANCE_NEEDED").

- [ ] **Task 2.2: AI 诊断文案生成**
  - 集成 LLM (Gemini).
  - 设计 Prompt: 输入 SKU 指标，输出一句话诊断 + 3 个具体 Action (提价/降价/否词).
  - 实现 `DiagnosisService.generate_report(sku_id)`.

## Phase 3: API 开发 (Backend)

- [x] **Task 3.1: 诊断大盘接口**
  - `GET /api/v1/ads/analysis/matrix`: 返回所有 SKU 的坐标 (X=Stock, Y=Performance) 和分类.
  - 支持筛选: `date_range`, `marketplace`.

- [x] **Task 3.2: SKU 详情接口**
  - `GET /api/v1/ads/analysis/{sku}/detail`: 返回该 SKU 的详细趋势图数据 (30天 ACOS/Stock 走势).
  - `GET /api/v1/ads/analysis/{sku}/diagnosis`: 返回 AI 生成的诊断建议.

- [ ] **Task 3.3: 成本录入接口**
  - `POST /api/v1/products/costs`: 批量更新 SKU 的 COGS.

## Phase 4: 前端开发 (Frontend - The Matrix)

- [x] **Task 4.1: 导航与布局**
  - 添加 "Ads Analysis" 侧边栏入口.
  - 创建主页面 `AdsAnalysisView.vue`.

- [x] **Task 4.2: 生意诊断矩阵组件 (The Matrix)**
  - 使用 ECharts 散点图 (Scatter Plot) 实现四象限视图.
  - X轴: 库存周转 (Weeks of Cover).
  - Y轴: 广告绩效 (TACOS).
  - 交互: 悬停显示 SKU 信息，点击选中 SKU.

- [x] **Task 4.3: 诊断详情面板**
  - 右侧抽屉 (Drawer) 组件.
  - 展示: 基础信息, 趋势图, **AI 诊断建议卡片**.
  - Action 按钮: "采纳建议" (Mock 交互).

- [ ] **Task 4.4: 成本录入表格**
  - 使用 Ag-Grid 或 DataTable 展示 SKU 列表.
  - 支持行内编辑 COGS 并保存.

## Phase 5: 集成与测试

- [x] **Task 5.1: 全链路联调**
  - 验证 Mock 数据 -> 后端计算 -> 前端展示 的完整流程.
- [ ] **Task 5.2: 单元测试**
  - 测试核心计算逻辑 (TACOS, 周转).
  - 测试象限分类准确性.
