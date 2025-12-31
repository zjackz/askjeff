# Smart Ads Diagnosis (智能广告诊断)

## 1. 背景与目标

本项目最初旨在构建一个类似 ERP 的广告管理系统。然而，为了提供更高的业务价值，我们将重心从**“繁杂的数据管理”**转移到了**“智能决策辅助”**。

**核心理念：**

* **Tell, Don't Ask**: 系统不应只展示数据列表让用户自己查找问题，而应直接告诉用户“问题在哪里”。
* **Action-Oriented**: 每一个诊断结果都应对应一个具体的行动（如：暂停、降价）。

## 2. 功能模块

### 2.1 无效花费拦截 (Wasted Spend Blocker)

**目标**：快速识别并停止那些只花钱不出单的“吸血”广告。

* **诊断逻辑**：
  * 时间范围：过去 7 天（可配置）
  * 筛选条件：`Spend > $50` (阈值可配) AND `Orders == 0`
* **后端实现**：
  * Service: `AdsDiagnosisService.check_wasted_spend`
  * API: `GET /api/v1/amazon/diagnosis/wasted-spend`
* **前端展示**：
  * 组件: `WastedSpendBlocker.vue`
  * 展示: 红色/警示风格，列出浪费金额总和及具体 Campaign。

### 2.2 高 ACOS 预警 (High ACOS Warning)

**目标**：识别获客成本过高、正在侵蚀利润的广告活动。

* **诊断逻辑**：
  * 时间范围：过去 7 天
  * 筛选条件：`Spend > $50` AND `ACOS > 30%` (阈值可配)
* **后端实现**：
  * Service: `AdsDiagnosisService.check_high_acos`
  * API: `GET /api/v1/amazon/diagnosis/high-acos`
* **前端展示**：
  * 组件: `HighAcosWarning.vue`
  * 展示: 黄色/警告风格，按 ACOS 降序排列。

## 3. 技术架构

### 3.1 后端 (FastAPI)

* **Service Layer**: `app/services/ads_diagnosis_service.py` 封装所有诊断算法，保持 Controller 层轻量。
* **Data Model**: 复用 `AdvertisingCampaign` 和 `CampaignPerformanceSnapshot`，利用 SQL 聚合查询 (`group_by`, `having`) 高效处理数据。
* **Schema**: 定义了 `WastedSpendResponse` 和 `HighAcosResponse` 等专用响应结构，与通用 CRUD 分离。

### 3.2 前端 (Vue 3 + TypeScript)

* **View**: `ActionsView.vue` 作为智能决策中心的主入口，采用 Grid 布局容器。
* **Components**: 每个诊断功能封装为独立组件 (`WastedSpendBlocker`, `HighAcosWarning`)，自包含数据获取逻辑，便于复用和扩展。
* **API Client**: `amazonAdsApi` 扩展了诊断相关的方法。

## 4. 后续规划 (Roadmap)

1. **闭环执行 (Action Execution)**:
    * 实现“一键暂停” (Pause All Wasted)。
    * 实现“一键降价” (Decrease Bid for High ACOS)。
2. **更多诊断维度**:
    * **预算不足 (Out of Budget)**: 每天下午就花光预算的广告。
    * **转化率暴跌 (CVR Drop)**: 流量正常但转化率突然下降的 Listing。
3. **趋势分析**:
    * 结合 `CampaignPerformanceSnapshot` 提供 ACOS 变化趋势图。
