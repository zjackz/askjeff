# Amazon Ads Analysis - 数据库设计方案

**版本**: v1.0  
**日期**: 2025-12-30  
**状态**: 设计阶段  

---

## 📋 设计原则

1. **多租户隔离**: 每个用户的数据完全隔离
2. **多店铺支持**: 单用户可管理多个亚马逊店铺
3. **多市场支持**: 支持全球不同 Marketplace
4. **数据可追溯**: 所有快照数据保留历史记录
5. **扩展性**: 预留字段支持未来功能扩展

---

## 🏗️ 核心表结构

### 1. amazon_stores (店铺表)

**用途**: 管理用户的亚马逊店铺信息

```sql
CREATE TABLE amazon_stores (
    -- 主键
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 用户关联
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 店铺基本信息
    store_name VARCHAR(255) NOT NULL,                    -- 自定义店铺名称
    marketplace_id VARCHAR(20) NOT NULL,                 -- ATVPDKIKX0DER (US), A1PA6795UKMFR9 (DE)
    marketplace_name VARCHAR(50) NOT NULL,               -- United States, Germany
    seller_id VARCHAR(50) NOT NULL,                      -- 卖家 ID
    
    -- API 凭证 (需加密存储)
    sp_api_refresh_token TEXT,                           -- SP-API 刷新令牌
    advertising_api_refresh_token TEXT,                  -- Advertising API 刷新令牌
    sp_api_client_id VARCHAR(255),                       -- LWA Client ID
    sp_api_client_secret VARCHAR(255),                   -- LWA Client Secret (加密)
    
    -- 状态管理
    is_active BOOLEAN NOT NULL DEFAULT TRUE,             -- 是否启用
    sync_status VARCHAR(20) DEFAULT 'idle',              -- idle, syncing, error
    last_sync_at TIMESTAMP WITH TIME ZONE,               -- 最后同步时间
    last_sync_error TEXT,                                -- 最后同步错误信息
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT uix_user_marketplace_seller UNIQUE (user_id, marketplace_id, seller_id)
);

CREATE INDEX idx_amazon_stores_user_id ON amazon_stores(user_id);
CREATE INDEX idx_amazon_stores_marketplace_id ON amazon_stores(marketplace_id);
CREATE INDEX idx_amazon_stores_is_active ON amazon_stores(is_active);
```

**字段说明**:

- `marketplace_id`: 亚马逊官方市场 ID，用于 API 调用
- `seller_id`: 唯一标识卖家账户
- `sp_api_refresh_token`: 用于获取 SP-API 访问令牌
- `advertising_api_refresh_token`: 用于获取广告 API 访问令牌
- `sync_status`: 数据同步状态，用于前端展示和任务调度

---

### 2. product_costs (产品成本表)

**用途**: 存储每个 SKU 的成本信息，用于计算净利润

```sql
CREATE TABLE product_costs (
    -- 主键
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 店铺关联
    store_id UUID NOT NULL REFERENCES amazon_stores(id) ON DELETE CASCADE,
    
    -- 产品标识
    sku VARCHAR(100) NOT NULL,                           -- 商家 SKU
    asin VARCHAR(20) NOT NULL,                           -- Amazon ASIN
    fnsku VARCHAR(20),                                   -- Fulfillment Network SKU
    
    -- 成本数据
    cogs DECIMAL(10, 2) NOT NULL,                        -- Cost of Goods Sold (采购成本)
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',          -- 货币单位
    
    -- Amazon 费用
    fba_fee DECIMAL(10, 2),                              -- FBA 配送费
    referral_fee_rate DECIMAL(5, 4),                     -- 佣金费率 (如 0.15 = 15%)
    storage_fee_monthly DECIMAL(10, 2),                  -- 月度仓储费
    
    -- 其他成本
    inbound_shipping_cost DECIMAL(10, 2),                -- 头程物流成本
    packaging_cost DECIMAL(10, 2),                       -- 包装成本
    
    -- 备注
    notes TEXT,                                          -- 成本备注
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT uix_store_sku UNIQUE (store_id, sku)
);

CREATE INDEX idx_product_costs_store_id ON product_costs(store_id);
CREATE INDEX idx_product_costs_sku ON product_costs(sku);
CREATE INDEX idx_product_costs_asin ON product_costs(asin);
```

**字段说明**:

- `cogs`: 核心成本，用于计算毛利
- `fba_fee`: 从 Amazon Fee Preview Report 获取
- `referral_fee_rate`: 不同类目费率不同 (8%-15%)
- `storage_fee_monthly`: 长期仓储费，影响库存决策

---

### 3. inventory_snapshots (库存快照表)

**用途**: 每日库存状态快照，用于计算库存周转和缺货风险

```sql
CREATE TABLE inventory_snapshots (
    -- 主键
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 店铺关联
    store_id UUID NOT NULL REFERENCES amazon_stores(id) ON DELETE CASCADE,
    
    -- 时间维度
    date DATE NOT NULL,                                  -- 快照日期
    
    -- 产品标识
    sku VARCHAR(100) NOT NULL,
    asin VARCHAR(20) NOT NULL,
    
    -- 库存数据 (从 FBA Inventory Report)
    fba_inventory INTEGER NOT NULL DEFAULT 0,            -- FBA 可售库存
    inbound_inventory INTEGER NOT NULL DEFAULT 0,        -- 在途库存
    reserved_inventory INTEGER NOT NULL DEFAULT 0,       -- 预留库存 (已下单未发货)
    unfulfillable_inventory INTEGER NOT NULL DEFAULT 0,  -- 不可售库存 (损坏/过期)
    
    -- 计算字段
    total_available INTEGER GENERATED ALWAYS AS (fba_inventory + inbound_inventory) STORED,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT uix_store_inventory_date_sku UNIQUE (store_id, date, sku)
);

CREATE INDEX idx_inventory_snapshots_store_id ON inventory_snapshots(store_id);
CREATE INDEX idx_inventory_snapshots_date ON inventory_snapshots(date);
CREATE INDEX idx_inventory_snapshots_sku ON inventory_snapshots(sku);
CREATE INDEX idx_inventory_snapshots_asin ON inventory_snapshots(asin);
```

**字段说明**:

- `fba_inventory`: 当前可售库存，核心指标
- `inbound_inventory`: 在途库存，用于预测未来可售量
- `reserved_inventory`: 已下单但未发货，实际不可售
- `total_available`: 计算字段，总可用库存

---

### 4. ads_metric_snapshots (广告指标快照表)

**用途**: 每日 SKU 级别的广告数据快照

```sql
CREATE TABLE ads_metric_snapshots (
    -- 主键
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 店铺关联
    store_id UUID NOT NULL REFERENCES amazon_stores(id) ON DELETE CASCADE,
    
    -- 时间维度
    date DATE NOT NULL,
    
    -- 产品标识
    sku VARCHAR(100) NOT NULL,
    asin VARCHAR(20) NOT NULL,
    
    -- 广告花费与销售
    spend DECIMAL(10, 2) NOT NULL DEFAULT 0.00,          -- 广告花费
    sales DECIMAL(10, 2) NOT NULL DEFAULT 0.00,          -- 广告销售额
    
    -- 流量数据
    impressions INTEGER NOT NULL DEFAULT 0,              -- 曝光量
    clicks INTEGER NOT NULL DEFAULT 0,                   -- 点击量
    
    -- 转化数据
    orders INTEGER NOT NULL DEFAULT 0,                   -- 订单数
    units INTEGER NOT NULL DEFAULT 0,                    -- 销售件数
    
    -- 计算指标 (可选，也可在查询时计算)
    acos DECIMAL(5, 4) GENERATED ALWAYS AS (
        CASE WHEN sales > 0 THEN spend / sales ELSE NULL END
    ) STORED,                                            -- ACOS = Spend / Sales
    
    ctr DECIMAL(5, 4) GENERATED ALWAYS AS (
        CASE WHEN impressions > 0 THEN clicks::DECIMAL / impressions ELSE NULL END
    ) STORED,                                            -- CTR = Clicks / Impressions
    
    cvr DECIMAL(5, 4) GENERATED ALWAYS AS (
        CASE WHEN clicks > 0 THEN orders::DECIMAL / clicks ELSE NULL END
    ) STORED,                                            -- CVR = Orders / Clicks
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT uix_store_ads_date_sku UNIQUE (store_id, date, sku)
);

CREATE INDEX idx_ads_metric_snapshots_store_id ON ads_metric_snapshots(store_id);
CREATE INDEX idx_ads_metric_snapshots_date ON ads_metric_snapshots(date);
CREATE INDEX idx_ads_metric_snapshots_sku ON ads_metric_snapshots(sku);
CREATE INDEX idx_ads_metric_snapshots_asin ON ads_metric_snapshots(asin);
```

**字段说明**:

- `spend`: 广告花费，核心成本
- `sales`: 广告带来的销售额
- `acos`: Advertising Cost of Sales，核心 KPI
- `ctr`: Click-Through Rate，衡量广告吸引力
- `cvr`: Conversion Rate，衡量转化能力

---

### 5. business_metric_snapshots (业务指标快照表)

**用途**: 每日 SKU 级别的整体业务数据 (包含自然流量)

```sql
CREATE TABLE business_metric_snapshots (
    -- 主键
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 店铺关联
    store_id UUID NOT NULL REFERENCES amazon_stores(id) ON DELETE CASCADE,
    
    -- 时间维度
    date DATE NOT NULL,
    
    -- 产品标识
    sku VARCHAR(100) NOT NULL,
    asin VARCHAR(20) NOT NULL,
    
    -- 销售数据
    total_sales_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,  -- 总销售额 (广告 + 自然)
    total_units_ordered INTEGER NOT NULL DEFAULT 0,           -- 总销量
    
    -- 流量数据
    sessions INTEGER NOT NULL DEFAULT 0,                      -- 访问量 (Session)
    page_views INTEGER NOT NULL DEFAULT 0,                    -- 页面浏览量
    
    -- 转化率
    unit_session_percentage DECIMAL(5, 4),                    -- 单位转化率 = Units / Sessions
    
    -- 退货数据 (可选)
    returns INTEGER DEFAULT 0,                                -- 退货数量
    return_rate DECIMAL(5, 4),                                -- 退货率
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT uix_store_biz_date_sku UNIQUE (store_id, date, sku)
);

CREATE INDEX idx_business_metric_snapshots_store_id ON business_metric_snapshots(store_id);
CREATE INDEX idx_business_metric_snapshots_date ON business_metric_snapshots(date);
CREATE INDEX idx_business_metric_snapshots_sku ON business_metric_snapshots(sku);
CREATE INDEX idx_business_metric_snapshots_asin ON business_metric_snapshots(asin);
```

**字段说明**:

- `total_sales_amount`: 总销售额，包含广告和自然流量
- `sessions`: 访问量，用于计算转化率
- `unit_session_percentage`: 核心转化指标

---

## 🔗 表关系图

```
users (现有表)
  │
  ├──> amazon_stores (1:N)
         │
         ├──> product_costs (1:N)
         ├──> inventory_snapshots (1:N)
         ├──> ads_metric_snapshots (1:N)
         └──> business_metric_snapshots (1:N)
```

---

## 📊 核心查询场景

### 场景 1: 计算 TACOS (Total ACOS)

```sql
SELECT 
    sku,
    SUM(ads.spend) AS total_ad_spend,
    SUM(biz.total_sales_amount) AS total_sales,
    SUM(ads.spend) / NULLIF(SUM(biz.total_sales_amount), 0) AS tacos
FROM ads_metric_snapshots ads
JOIN business_metric_snapshots biz 
    ON ads.store_id = biz.store_id 
    AND ads.date = biz.date 
    AND ads.sku = biz.sku
WHERE ads.store_id = :store_id
    AND ads.date >= :start_date
    AND ads.date <= :end_date
GROUP BY sku;
```

### 场景 2: 计算库存周转 (Weeks of Cover)

```sql
SELECT 
    inv.sku,
    inv.fba_inventory,
    AVG(biz.total_units_ordered) AS avg_daily_sales,
    CASE 
        WHEN AVG(biz.total_units_ordered) > 0 
        THEN inv.fba_inventory / (AVG(biz.total_units_ordered) * 7)
        ELSE NULL 
    END AS weeks_of_cover
FROM inventory_snapshots inv
JOIN business_metric_snapshots biz 
    ON inv.store_id = biz.store_id 
    AND inv.sku = biz.sku
WHERE inv.store_id = :store_id
    AND inv.date = :current_date
    AND biz.date >= :start_date
    AND biz.date <= :end_date
GROUP BY inv.sku, inv.fba_inventory;
```

### 场景 3: 四象限分类

```sql
WITH metrics AS (
    SELECT 
        sku,
        weeks_of_cover,
        tacos,
        CASE 
            WHEN weeks_of_cover > 24 AND tacos > 0.20 THEN 'CRITICAL / CLEARANCE'
            WHEN weeks_of_cover > 24 AND tacos <= 0.20 THEN 'STAR / GROWTH'
            WHEN weeks_of_cover <= 24 AND tacos <= 0.20 THEN 'POTENTIAL / DEFENSE'
            ELSE 'DROP / KILL'
        END AS quadrant
    FROM (
        -- 子查询计算 weeks_of_cover 和 tacos
    ) t
)
SELECT * FROM metrics;
```

---

## 🔐 数据安全

### 敏感字段加密

以下字段需要在应用层加密后存储：

- `sp_api_refresh_token`
- `advertising_api_refresh_token`
- `sp_api_client_secret`

**推荐方案**: 使用 `cryptography.fernet` 对称加密

```python
from cryptography.fernet import Fernet

# 初始化 (密钥存储在环境变量)
cipher = Fernet(os.getenv('ENCRYPTION_KEY'))

# 加密
encrypted_token = cipher.encrypt(refresh_token.encode())

# 解密
decrypted_token = cipher.decrypt(encrypted_token).decode()
```

---

## 📈 性能优化

### 1. 分区表 (未来优化)

当数据量超过 1000 万行时，考虑按日期分区：

```sql
CREATE TABLE inventory_snapshots (
    ...
) PARTITION BY RANGE (date);

CREATE TABLE inventory_snapshots_2025_01 
    PARTITION OF inventory_snapshots
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### 2. 物化视图 (预计算)

对于频繁查询的聚合数据，可以创建物化视图：

```sql
CREATE MATERIALIZED VIEW mv_sku_metrics_30d AS
SELECT 
    store_id,
    sku,
    SUM(spend) AS total_spend,
    SUM(sales) AS total_sales,
    AVG(acos) AS avg_acos
FROM ads_metric_snapshots
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY store_id, sku;

CREATE INDEX ON mv_sku_metrics_30d(store_id, sku);
```

### 3. 索引策略

- **复合索引**: `(store_id, date, sku)` 覆盖大部分查询
- **部分索引**: 只索引活跃店铺的数据

  ```sql
  CREATE INDEX idx_active_stores 
  ON amazon_stores(user_id) 
  WHERE is_active = TRUE;
  ```

---

## 🚀 扩展性设计

### 未来可能的扩展

1. **Campaign 级别数据**: 新增 `ads_campaign_snapshots` 表
2. **Keyword 级别数据**: 新增 `ads_keyword_snapshots` 表
3. **Product 级别元数据**: 新增 `products` 表存储标题、图片、类目等
4. **Alert 规则**: 新增 `alert_rules` 表支持自定义告警

---

## ✅ 设计检查清单

- [x] 支持多租户隔离
- [x] 支持多店铺管理
- [x] 支持多市场
- [x] 数据可追溯 (快照表)
- [x] 外键约束完整
- [x] 索引覆盖主要查询
- [x] 敏感数据加密方案
- [x] 性能优化预案
- [x] 扩展性预留

---

**审核状态**: ⏳ 待审核  
**审核人**: -  
**审核日期**: -
