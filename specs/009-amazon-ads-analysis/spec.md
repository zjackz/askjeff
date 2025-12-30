# 需求规格: 009 - Amazon Ads Analysis & Optimization

**需求编号**: 009  
**创建日期**: 2025-12-30  
**优先级**: P0 (核心功能)  
**负责人**: AI Agent  

---

## 📋 背景与目标

### 核心问题

亚马逊卖家在广告优化时面临的核心痛点：

1. **数据孤岛**: 广告数据、库存数据、业务报表分散在不同系统
2. **决策困难**: 面对海量原始数据，不知道该优化哪个 SKU
3. **归因滞后**: 广告调整后，需要等待数周才能看到库存影响

### 解决方案

提供一个 **"诊断 + 优化"** 的一体化工具，核心特点：

- **库存联动**: 将广告表现与库存状态结合，避免"爆单断货"或"积压滞销"
- **可视化诊断**: 通过"上帝视角"的四象限矩阵，一眼看出问题 SKU
- **AI 建议**: 基于规则引擎 + LLM，生成具体的优化策略（调价/调预算/否词）

---

## 🏗️ 架构设计

### 多租户 & 多店铺支持

**企业级架构特性**:

- ✅ **多用户隔离**: 每个用户拥有独立的数据空间
- ✅ **多店铺管理**: 单个用户可管理多个亚马逊店铺
- ✅ **多市场支持**: 支持美国、欧洲、日本等不同 Marketplace
- ✅ **API 凭证管理**: 安全存储每个店铺的 SP-API 和 Advertising API Token

### 数据模型

#### 1. AmazonStore (店铺表)

```python
- user_id: 用户 ID (外键)
- store_name: 店铺名称 (自定义)
- marketplace_id: 市场 ID (如 ATVPDKIKX0DER for US)
- marketplace_name: 市场名称 (如 United States)
- seller_id: 卖家 ID
- sp_api_refresh_token: SP-API 刷新令牌 (加密)
- advertising_api_refresh_token: 广告 API 刷新令牌 (加密)
- is_active: 是否启用
- last_sync_at: 最后同步时间
```

#### 2. ProductCost (成本表)

```python
- store_id: 店铺 ID (外键)
- sku: 商品 SKU
- asin: ASIN
- cogs: 成本
- fba_fee: FBA 费用
- referral_fee_rate: 佣金费率
```

#### 3. InventorySnapshot (库存快照)

```python
- store_id: 店铺 ID
- date: 日期
- sku: SKU
- fba_inventory: FBA 可售库存
- inbound_inventory: 在途库存
- reserved_inventory: 预留库存
- unfulfillable_inventory: 不可售库存
```

#### 4. AdsMetricSnapshot (广告快照)

```python
- store_id: 店铺 ID
- date: 日期
- sku: SKU
- spend: 广告花费
- sales: 广告销售额
- impressions: 曝光量
- clicks: 点击量
- orders: 订单数
- units: 销售件数
```

#### 5. BusinessMetricSnapshot (业务快照)

```python
- store_id: 店铺 ID
- date: 日期
- sku: SKU
- total_sales_amount: 总销售额
- total_units_ordered: 总销量
- sessions: 访问量
- page_views: 页面浏览量
- unit_session_percentage: 单位转化率
```

---

- **决策困难**: 只有数据没有结论，运营人员不知道如何调整。
- **归因延迟**: 官方数据有延迟，难以实时决策。

## 4. 功能需求 (MVP)

### 4.1 数据层 (Data Layer)

- **多源数据聚合**:
  - **广告数据**: Campaign, AdGroup, Keyword, Search Term (Spend, Sales, Impressions, Clicks, CPC).
  - **业务数据**: Total Sales (用于计算 TACOS), Sessions (流量).
  - **库存数据**: FBA Inventory, Inbound (在途).
- **指标计算**:
  - ACOS, TACOS, ROAS.
  - 预计销售月数 (Weeks of Cover).
  - 广告销售贡献比.

### 4.2 诊断模块 (Diagnosis Engine)

- **SKU级诊断表**:
  - 维度: SKU/ASIN.
  - 指标: 尺寸/变体, ACOS, TACOS, 预计销售月数.
  - **智能结论输出** (基于规则 + AI):
    - *主力款积压*: "激进推广"
    - *潜力爆款*: "适当增投"
    - *滞销款*: "降价清仓"
    - *严重滞销*: "大力清仓"

### 4.3 优化模块 (Optimization)

- **建议生成**:
  - 竞价建议 (提价/降价).
  - 预算建议.
  - 否定词建议 (高点击低转化).
- **AI 赋能**:
  - 使用 LLM 解读数据报告，生成自然语言诊断书。

## 5. 竞品分析与差异化

- **竞品**: Perpetua, Helium10, SellerSprite.
- **差异化**: 专注于 "库存周转 x 广告绩效" 的联合诊断，提供类似"体检报告"的决策辅助，而非单纯的自动投放工具。

## 6. 数据流图

```mermaid
graph TD
    A[Amazon Ads API] --> D[Data Warehouse]
    B[Amazon SP-API (Inventory/Sales)] --> D
    D --> E[Analysis Engine]
    E --> F[Diagnosis Matrix (Inventory vs ACOS)]
    F --> G[AI Advisor (LLM)]
    G --> H[Dashboard / Action Plan]
```

## 7. 技术可行性

- **API**: Amazon Advertising API + SP-API.
- **挑战**:
  - 报告数据的实时性与准确性。
  - 跨API的数据对齐 (SKU Mapping).
