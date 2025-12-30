# Amazon Ads Analysis - 单元测试文档

**创建日期**: 2025-12-30  
**测试覆盖率目标**: 90%+  

---

## 📋 测试文件概览

### 1. `test_ads_analysis_service.py`

**Service 层单元测试** - 测试业务逻辑核心

#### 测试类

- `TestAdsAnalysisService` - Service 核心功能测试
- `TestMetricsCalculation` - 指标计算准确性测试
- `TestEdgeCases` - 边界情况测试

#### 测试用例 (共 18 个)

**权限验证测试**:

- ✅ `test_verify_store_access_success` - 验证成功场景
- ✅ `test_verify_store_access_wrong_user` - 错误用户访问
- ✅ `test_verify_store_access_nonexistent_store` - 不存在的店铺

**店铺列表测试**:

- ✅ `test_get_user_stores` - 获取用户店铺列表
- ✅ `test_get_user_stores_empty` - 空店铺列表

**矩阵数据测试**:

- ✅ `test_get_matrix_data` - 获取矩阵数据
- ✅ `test_get_matrix_data_wrong_user` - 错误用户访问矩阵

**分类逻辑测试**:

- ✅ `test_classify_sku_critical` - Critical 分类
- ✅ `test_classify_sku_star` - Star 分类
- ✅ `test_classify_sku_potential` - Potential 分类
- ✅ `test_classify_sku_drop` - Drop 分类
- ✅ `test_classify_sku_boundary_conditions` - 边界条件

**诊断生成测试**:

- ✅ `test_generate_diagnosis_critical` - Critical 诊断
- ✅ `test_generate_diagnosis_star` - Star 诊断
- ✅ `test_generate_diagnosis_potential` - Potential 诊断
- ✅ `test_generate_diagnosis_drop` - Drop 诊断

**指标计算测试**:

- ✅ `test_tacos_calculation` - TACOS 计算准确性
- ✅ `test_weeks_of_cover_calculation` - 库存周转计算准确性

**边界情况测试**:

- ✅ `test_zero_sales` - 零销量场景
- ✅ `test_no_inventory` - 零库存场景

---

### 2. `test_ads_analysis_api.py`

**API 层集成测试** - 测试端点和权限控制

#### 测试类

- `TestStoresAPI` - 店铺列表 API
- `TestMatrixAPI` - 矩阵数据 API
- `TestDiagnosisAPI` - 诊断 API
- `TestCrossStoreIsolation` - 跨店铺隔离
- `TestPerformance` - 性能测试

#### 测试用例 (共 17 个)

**店铺 API 测试**:

- ✅ `test_get_stores_success` - 成功获取店铺列表
- ✅ `test_get_stores_unauthorized` - 未认证访问
- ✅ `test_get_stores_empty` - 空店铺列表

**矩阵 API 测试**:

- ✅ `test_get_matrix_success` - 成功获取矩阵数据
- ✅ `test_get_matrix_missing_store_id` - 缺少 store_id
- ✅ `test_get_matrix_invalid_store_id` - 无效 store_id
- ✅ `test_get_matrix_unauthorized` - 未认证访问
- ✅ `test_get_matrix_with_custom_days` - 自定义天数
- ✅ `test_get_matrix_days_validation` - 天数参数验证

**诊断 API 测试**:

- ✅ `test_get_diagnosis_success` - 成功获取诊断
- ✅ `test_get_diagnosis_sku_not_found` - SKU 不存在
- ✅ `test_get_diagnosis_missing_store_id` - 缺少 store_id
- ✅ `test_get_diagnosis_unauthorized` - 未认证访问

**安全性测试**:

- ✅ `test_cannot_access_other_user_store` - 跨用户隔离

**性能测试**:

- ✅ `test_matrix_response_time` - 响应时间 < 2s

---

### 3. `test_ads_models.py`

**数据模型测试** - 测试数据库约束和关系

#### 测试类

- `TestAmazonStoreModel` - 店铺模型
- `TestProductCostModel` - 成本模型
- `TestInventorySnapshotModel` - 库存快照模型
- `TestAdsMetricSnapshotModel` - 广告快照模型
- `TestBusinessMetricSnapshotModel` - 业务快照模型
- `TestCascadeDelete` - 级联删除测试

#### 测试用例 (共 11 个)

**店铺模型测试**:

- ✅ `test_create_store` - 创建店铺
- ✅ `test_store_unique_constraint` - 唯一约束
- ✅ `test_store_foreign_key` - 外键约束

**成本模型测试**:

- ✅ `test_create_product_cost` - 创建成本
- ✅ `test_product_cost_unique_constraint` - 唯一约束

**快照模型测试**:

- ✅ `test_create_inventory_snapshot` - 创建库存快照
- ✅ `test_inventory_snapshot_unique_constraint` - 唯一约束
- ✅ `test_create_ads_snapshot` - 创建广告快照
- ✅ `test_create_business_snapshot` - 创建业务快照

**级联删除测试**:

- ✅ `test_delete_store_cascades_to_costs` - 级联删除成本
- ✅ `test_delete_store_cascades_to_snapshots` - 级联删除快照

---

## 🎯 测试覆盖范围

### Service 层覆盖

- ✅ 权限验证逻辑
- ✅ 数据查询和聚合
- ✅ SKU 分类算法
- ✅ 诊断生成逻辑
- ✅ 指标计算准确性
- ✅ 边界情况处理

### API 层覆盖

- ✅ 所有 3 个端点
- ✅ 认证和授权
- ✅ 参数验证
- ✅ 错误处理
- ✅ 跨租户隔离
- ✅ 响应时间

### 数据层覆盖

- ✅ 所有 5 个模型
- ✅ 唯一约束
- ✅ 外键约束
- ✅ 级联删除
- ✅ 数据完整性

---

## 🚀 运行测试

### 运行所有广告模块测试

```bash
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_*.py -v
```

### 运行特定测试文件

```bash
# Service 层测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_analysis_service.py -v

# API 层测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_analysis_api.py -v

# 模型测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_models.py -v
```

### 生成覆盖率报告

```bash
docker exec askjeff-dev-backend-1 poetry run pytest tests/test_ads_*.py \
  --cov=app.services.ads_analysis_service \
  --cov=app.api.v1.endpoints.ads_analysis \
  --cov=app.models.amazon_ads \
  --cov-report=html \
  --cov-report=term
```

### 运行特定测试用例

```bash
# 运行单个测试
docker exec askjeff-dev-backend-1 poetry run pytest \
  tests/test_ads_analysis_service.py::TestAdsAnalysisService::test_get_matrix_data -v

# 运行测试类
docker exec askjeff-dev-backend-1 poetry run pytest \
  tests/test_ads_analysis_api.py::TestMatrixAPI -v
```

---

## 📊 测试统计

| 测试文件 | 测试类 | 测试用例 | 覆盖模块 |
|---------|--------|---------|---------|
| `test_ads_analysis_service.py` | 3 | 18 | Service 层 |
| `test_ads_analysis_api.py` | 5 | 17 | API 层 |
| `test_ads_models.py` | 6 | 11 | 数据模型 |
| **总计** | **14** | **46** | **全模块** |

---

## ✅ 测试清单

### 功能测试

- [x] 店铺权限验证
- [x] 矩阵数据查询
- [x] SKU 分类逻辑
- [x] 诊断生成
- [x] TACOS 计算
- [x] 库存周转计算

### 安全测试

- [x] 用户认证
- [x] 跨租户隔离
- [x] 权限控制
- [x] 参数验证

### 数据完整性测试

- [x] 唯一约束
- [x] 外键约束
- [x] 级联删除
- [x] 数据类型验证

### 边界测试

- [x] 零销量
- [x] 零库存
- [x] 空数据集
- [x] 边界值

### 性能测试

- [x] API 响应时间
- [ ] 大数据集查询 (待添加)
- [ ] 并发请求 (待添加)

---

## 🔧 测试 Fixtures

### 通用 Fixtures

- `db` - 数据库会话 (pytest-sqlalchemy)
- `client` - FastAPI 测试客户端
- `test_user` - 测试用户
- `test_user_with_password` - 带密码的测试用户
- `auth_headers` - 认证 headers

### 广告模块 Fixtures

- `test_store` - 测试店铺
- `test_sku_data` - 测试 SKU 数据 (30 天快照)
- `test_store_with_data` - 带完整数据的测试店铺 (3 SKU)

---

## 📝 待添加测试

### 高优先级

- [ ] 大数据集性能测试 (1000+ SKU)
- [ ] 并发请求测试
- [ ] 日期范围筛选测试
- [ ] 多店铺数据隔离测试

### 中优先级

- [ ] Mock 数据生成器测试
- [ ] Schema 验证测试
- [ ] 错误消息国际化测试

### 低优先级

- [ ] 压力测试
- [ ] 内存泄漏测试
- [ ] 数据库连接池测试

---

## 🐛 已知问题

无

---

## 📚 参考资料

- [Pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试指南](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy 测试最佳实践](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

---

**最后更新**: 2025-12-30  
**维护者**: AI Agent
