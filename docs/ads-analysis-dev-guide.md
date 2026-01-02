# 广告分析模块 - 快速开发指南

**模块**: Amazon Ads Analysis & Optimization  
**当前版本**: v0.9.0 (90% 完成)  
**最后更新**: 2025-12-31

---

## 🚀 快速启动

### 启动系统

```bash
# 启动所有服务
make up

# 查看服务状态
make ps

# 查看后端日志
make backend-logs

# 查看前端日志
make frontend-logs
```

### 访问系统

- **前端**: http://localhost:5174
- **后端 API**: http://localhost:8001
- **广告诊断页面**: http://localhost:5174/ads-analysis

---

## 📁 项目结构

### 后端 (Backend)

```
backend/app/
├── api/v1/endpoints/
│   └── ads_analysis.py          # API 路由
├── services/
│   ├── ads_analysis_service.py  # 核心业务逻辑
│   ├── ads_ai_service.py        # AI 诊断服务
│   └── ai/deepseek_client.py    # LLM 客户端
├── models/
│   └── amazon_ads.py            # 数据模型
└── schemas/
    └── amazon_ads.py            # Pydantic Schema
```

### 前端 (Frontend)

```
frontend/src/views/ads-analysis/
├── index.vue                    # 主页面
├── MatrixView.vue               # 矩阵视图
├── OverviewView.vue             # 概览视图
├── ActionsView.vue              # 决策视图
└── components/
    ├── StoreSelector.vue        # 店铺选择器
    ├── AdsMatrixChart.vue       # ECharts 图表
    └── DiagnosisPanel.vue       # AI 诊断面板
```

---

## 🔧 常用开发命令

### 后端开发

```bash
# 进入后端容器
make shell-backend

# 运行测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_analysis_service.py -v

# 查看路由
docker exec askjeff-dev-backend-1 python scripts/print_routes.py | grep ads

# 生成 Mock 数据
docker exec askjeff-dev-backend-1 python scripts/mock_ads_data.py
```

### 前端开发

```bash
# 进入前端容器
make shell-frontend

# 运行 Lint
make lint-frontend

# 构建生产版本
docker exec askjeff-dev-frontend-1 pnpm build
```

### 数据库操作

```bash
# 进入数据库
docker exec -it askjeff-dev-db-1 psql -U postgres -d askjeff

# 查看店铺
SELECT id, store_name, marketplace_name FROM amazon_stores;

# 查看库存快照
SELECT date, sku, fba_inventory FROM inventory_snapshots LIMIT 10;

# 查看广告快照
SELECT date, sku, spend, sales FROM ads_metric_snapshots LIMIT 10;
```

---

## 📊 核心 API 端点

### 1. 获取店铺列表

```http
GET /api/v1/ads-analysis/stores
Authorization: Bearer {token}
```

**响应**:

```json
[
  {
    "id": "uuid",
    "store_name": "My Store",
    "marketplace_name": "United States",
    "seller_id": "A123456",
    "is_active": true
  }
]
```

### 2. 获取矩阵数据

```http
GET /api/v1/ads-analysis/matrix?store_id={uuid}&days=30
Authorization: Bearer {token}
```

**响应**:

```json
[
  {
    "sku": "SKU-001",
    "asin": "B00123456",
    "stock_weeks": 32.5,
    "tacos": 28.3,
    "sales": 1250.00,
    "status": "CRITICAL / CLEARANCE",
    "ctr": 0.35,
    "cvr": 6.8,
    "acos": 35.2,
    "roas": 2.84,
    "margin": -5.2
  }
]
```

### 3. 获取 SKU 诊断

```http
GET /api/v1/ads-analysis/{sku}/diagnosis?store_id={uuid}
Authorization: Bearer {token}
```

**响应**:

```json
{
  "sku": "SKU-001",
  "asin": "B00123456",
  "status": "CRITICAL / CLEARANCE",
  "diagnosis": "【紧急清仓】SKU-001 库存积压严重且广告亏损...",
  "metrics": {
    "stock_weeks": 32.5,
    "tacos": 28.3,
    ...
  }
}
```

---

## 🎯 核心业务逻辑

### SKU 分类规则

```python
# 四象限分类
if stock_weeks > 24:
    if tacos > 20:
        return "CRITICAL / CLEARANCE"  # 积压清仓
    else:
        return "STAR / GROWTH"         # 明星增长
else:
    if tacos <= 20:
        return "POTENTIAL / DEFENSE"   # 潜力防御
    else:
        return "DROP / KILL"           # 淘汰清理
```

### 关键指标计算

```python
# TACOS (Total ACOS)
TACOS = (总广告花费 / 总销售额) × 100%

# 库存周转 (Weeks of Cover)
Weeks_of_Cover = 当前库存 / (日均销量 × 7)

# ACOS (Advertising Cost of Sales)
ACOS = (广告花费 / 广告销售额) × 100%

# ROAS (Return on Ad Spend)
ROAS = 广告销售额 / 广告花费

# CTR (Click-Through Rate)
CTR = (点击数 / 曝光数) × 100%

# CVR (Conversion Rate)
CVR = (订单数 / 点击数) × 100%
```

---

## 🧪 测试指南

### 运行所有测试

```bash
# 后端测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/ -v

# 广告分析模块测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_analysis_service.py -v

# 数据模型测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_models.py -v
```

### 测试覆盖率

```bash
docker exec askjeff-dev-backend-1 poetry run pytest tests/ --cov=app --cov-report=html
```

---

## 🐛 常见问题

### 1. 前端无法获取店铺列表

**问题**: 404 Not Found  
**解决**:

```bash
# 检查路由注册
docker exec askjeff-dev-backend-1 python scripts/print_routes.py | grep ads-analysis

# 检查后端日志
make backend-logs
```

### 2. AI 诊断不显示

**问题**: DeepSeek API 调用失败  
**解决**:

```bash
# 检查环境变量
docker exec askjeff-dev-backend-1 env | grep DEEPSEEK

# 查看后端日志
make backend-logs | grep "AI Diagnosis"
```

### 3. 矩阵图无数据

**问题**: 数据库无 Mock 数据  
**解决**:

```bash
# 生成 Mock 数据
docker exec askjeff-dev-backend-1 python scripts/mock_ads_data.py
```

---

## 📝 待办事项 (TODO)

### 优先级 P0 (本周)

- [ ] 修复测试导入错误
- [ ] 运行单元测试
- [ ] 浏览器功能测试
- [ ] 前端错误处理优化

### 优先级 P1 (下周)

- [ ] COGS 成本录入功能
- [ ] 日期范围筛选
- [ ] 诊断缓存 (Redis)
- [ ] 诊断历史记录

### 优先级 P2 (后续)

- [ ] Amazon SP-API 集成
- [ ] Advertising API 集成
- [ ] 定时同步任务
- [ ] 导出报告 (PDF/Excel)

---

## 📚 相关文档

- [需求规格](../specs/009-amazon-ads-analysis/spec.md)
- [开发计划](../specs/009-amazon-ads-analysis/plan.md)
- [进度跟踪](../specs/009-amazon-ads-analysis/progress.md)
- [数据库设计](../specs/009-amazon-ads-analysis/database-design.md)
- [竞品分析](../specs/009-amazon-ads-analysis/competitor_analysis.md)

---

## 🎓 学习资源

### Amazon Advertising API

- [官方文档](https://advertising.amazon.com/API/docs)
- [SP-API 文档](https://developer-docs.amazon.com/sp-api/)

### DeepSeek LLM

- [API 文档](https://platform.deepseek.com/api-docs/)
- [最佳实践](https://platform.deepseek.com/docs/best-practices)

### ECharts

- [官方文档](https://echarts.apache.org/zh/index.html)
- [散点图示例](https://echarts.apache.org/examples/zh/index.html#chart-type-scatter)

---

**最后更新**: 2025-12-31  
**维护者**: AI Agent
