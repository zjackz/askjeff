# Feature 001: 数据自动同步 - 开发任务清单

**功能编号**: ADS-001  
**开始日期**: 2026-01-02  
**预计完成**: 2026-01-09 (7 个工作日)  
**负责人**: Backend Team

---

## 📋 任务分解

### Phase 1: 基础设施搭建 (Day 1-2)

#### Task 1.1: Celery 环境配置 ⏱️ 4h

**描述**: 安装和配置 Celery + Redis

**子任务**:

- [ ] 安装依赖包

  ```bash
  poetry add celery redis
  ```

- [ ] 创建 Celery 应用配置
  - 文件: `backend/app/celery_app.py`
  - 配置 broker (Redis)
  - 配置 result backend
- [ ] 配置 Celery Beat (定时任务)
  - 文件: `backend/app/celeryconfig.py`
  - 定义定时任务调度
- [ ] 更新 Docker Compose
  - 添加 Redis 服务
  - 添加 Celery Worker 服务
  - 添加 Celery Beat 服务
- [ ] 编写启动脚本
  - `scripts/start_celery_worker.sh`
  - `scripts/start_celery_beat.sh`

**验收标准**:

- [ ] Celery Worker 正常启动
- [ ] Celery Beat 正常启动
- [ ] Redis 连接正常
- [ ] 可以执行测试任务

**相关文件**:

- `backend/app/celery_app.py` (新建)
- `backend/app/celeryconfig.py` (新建)
- `infra/docker/compose.dev.yml` (修改)

---

#### Task 1.2: 数据库表设计 ⏱️ 2h

**描述**: 创建 sync_tasks 表

**子任务**:

- [ ] 设计表结构

  ```sql
  CREATE TABLE sync_tasks (
      id UUID PRIMARY KEY,
      store_id UUID NOT NULL,
      sync_type VARCHAR(50),
      status VARCHAR(20),
      start_time TIMESTAMP,
      end_time TIMESTAMP,
      records_synced INTEGER,
      records_failed INTEGER,
      error_message TEXT,
      retry_count INTEGER,
      created_at TIMESTAMP
  );
  ```

- [ ] 创建 SQLAlchemy 模型
  - 文件: `backend/app/models/amazon_ads.py`
  - 添加 `SyncTask` 模型
- [ ] 创建 Alembic 迁移脚本

  ```bash
  alembic revision -m "add_sync_tasks_table"
  ```

- [ ] 运行迁移

  ```bash
  alembic upgrade head
  ```

**验收标准**:

- [ ] 表创建成功
- [ ] 索引创建正确
- [ ] 外键约束正常

**相关文件**:

- `backend/app/models/amazon_ads.py` (修改)
- `backend/alembic/versions/xxx_add_sync_tasks.py` (新建)

---

#### Task 1.3: Amazon API 客户端基类 ⏱️ 4h

**描述**: 创建 Amazon API 客户端基类

**子任务**:

- [ ] 创建基类
  - 文件: `backend/app/clients/amazon/base_client.py`
  - 实现 OAuth 令牌管理
  - 实现令牌自动刷新
  - 实现错误处理
- [ ] 编写单元测试
  - 文件: `backend/tests/clients/test_base_client.py`
  - 测试令牌获取
  - 测试令牌刷新
  - 测试错误处理
- [ ] 配置环境变量
  - `AMAZON_CLIENT_ID`
  - `AMAZON_CLIENT_SECRET`
  - `AMAZON_API_BASE_URL`

**验收标准**:

- [ ] 令牌获取成功
- [ ] 令牌自动刷新
- [ ] 单元测试通过 (覆盖率 > 80%)

**相关文件**:

- `backend/app/clients/amazon/__init__.py` (新建)
- `backend/app/clients/amazon/base_client.py` (新建)
- `backend/tests/clients/test_base_client.py` (新建)

---

### Phase 2: SP-API 集成 (Day 3-4)

#### Task 2.1: SP-API 客户端实现 ⏱️ 6h

**描述**: 实现 SP-API 客户端

**子任务**:

- [ ] 创建 SP-API 客户端
  - 文件: `backend/app/clients/amazon/sp_api_client.py`
  - 继承 `AmazonBaseClient`
- [ ] 实现库存报告获取
  - `fetch_inventory_report(start_date, end_date)`
  - 创建报告请求
  - 轮询报告状态
  - 下载报告
  - 解析 CSV 数据
- [ ] 实现业务报告获取
  - `fetch_business_report(start_date, end_date)`
  - 类似库存报告流程
- [ ] 实现数据解析器
  - `_parse_inventory_report(csv_data)`
  - `_parse_business_report(json_data)`
- [ ] 编写单元测试
  - Mock Amazon API 响应
  - 测试报告创建
  - 测试报告下载
  - 测试数据解析

**验收标准**:

- [ ] 可以成功获取库存报告
- [ ] 可以成功获取业务报告
- [ ] 数据解析正确
- [ ] 单元测试通过

**相关文件**:

- `backend/app/clients/amazon/sp_api_client.py` (新建)
- `backend/tests/clients/test_sp_api_client.py` (新建)

---

#### Task 2.2: 库存数据同步服务 ⏱️ 4h

**描述**: 实现库存数据同步服务

**子任务**:

- [ ] 创建同步服务
  - 文件: `backend/app/services/amazon_sync_service.py`
  - 实现 `sync_inventory(store_id, days)`
- [ ] 实现数据保存逻辑
  - Upsert 操作 (更新或插入)
  - 批量保存优化
- [ ] 实现任务状态管理
  - 创建任务记录
  - 更新任务状态
  - 记录错误信息
- [ ] 实现重试逻辑
  - 网络错误重试
  - 重试次数限制
  - 重试间隔控制
- [ ] 编写单元测试
  - 测试正常同步
  - 测试增量更新
  - 测试错误处理
  - 测试重试机制

**验收标准**:

- [ ] 库存数据同步成功
- [ ] 增量更新正确
- [ ] 错误处理完善
- [ ] 单元测试通过

**相关文件**:

- `backend/app/services/amazon_sync_service.py` (新建)
- `backend/tests/services/test_amazon_sync_service.py` (新建)

---

#### Task 2.3: 业务报告同步服务 ⏱️ 3h

**描述**: 实现业务报告同步服务

**子任务**:

- [ ] 实现 `sync_business_reports(store_id, days)`
- [ ] 数据映射和保存
- [ ] 编写单元测试

**验收标准**:

- [ ] 业务报告同步成功
- [ ] 数据映射正确
- [ ] 单元测试通过

**相关文件**:

- `backend/app/services/amazon_sync_service.py` (修改)
- `backend/tests/services/test_amazon_sync_service.py` (修改)

---

### Phase 3: Advertising API 集成 (Day 5-6)

#### Task 3.1: Advertising API 客户端 ⏱️ 6h

**描述**: 实现 Advertising API 客户端

**子任务**:

- [ ] 创建 Ads API 客户端
  - 文件: `backend/app/clients/amazon/ads_api_client.py`
  - 继承 `AmazonBaseClient`
- [ ] 实现 Campaign 报告获取
  - `fetch_campaign_report(start_date, end_date)`
- [ ] 实现 Search Term 报告获取
  - `fetch_search_term_report(start_date, end_date)`
- [ ] 实现数据聚合
  - 按 SKU 聚合 Campaign 数据
  - 计算汇总指标
- [ ] 编写单元测试

**验收标准**:

- [ ] 可以获取广告报告
- [ ] 数据聚合正确
- [ ] 单元测试通过

**相关文件**:

- `backend/app/clients/amazon/ads_api_client.py` (新建)
- `backend/tests/clients/test_ads_api_client.py` (新建)

---

#### Task 3.2: 广告数据同步服务 ⏱️ 4h

**描述**: 实现广告数据同步服务

**子任务**:

- [ ] 实现 `sync_advertising(store_id, days)`
- [ ] 数据映射和保存
- [ ] 编写单元测试

**验收标准**:

- [ ] 广告数据同步成功
- [ ] 数据映射正确
- [ ] 单元测试通过

**相关文件**:

- `backend/app/services/amazon_sync_service.py` (修改)
- `backend/tests/services/test_amazon_sync_service.py` (修改)

---

### Phase 4: 定时任务和 API (Day 7)

#### Task 4.1: Celery 任务定义 ⏱️ 3h

**描述**: 定义 Celery 异步任务

**子任务**:

- [ ] 创建任务文件
  - 文件: `backend/app/tasks/sync_tasks.py`
- [ ] 定义库存同步任务

  ```python
  @shared_task
  def sync_inventory_task(store_id: str, days: int = 30):
      pass
  ```

- [ ] 定义业务报告同步任务
- [ ] 定义广告数据同步任务
- [ ] 配置定时调度
  - 库存: 每日 2:00
  - 业务: 每日 2:30
  - 广告: 每日 3:00
- [ ] 编写任务测试

**验收标准**:

- [ ] 任务可以手动触发
- [ ] 任务可以定时触发
- [ ] 任务执行成功

**相关文件**:

- `backend/app/tasks/__init__.py` (新建)
- `backend/app/tasks/sync_tasks.py` (新建)
- `backend/app/celeryconfig.py` (修改)

---

#### Task 4.2: REST API 端点 ⏱️ 3h

**描述**: 创建同步相关的 API 端点

**子任务**:

- [ ] 创建路由文件
  - 文件: `backend/app/api/v1/endpoints/amazon_sync.py`
- [ ] 实现手动触发同步

  ```python
  POST /api/v1/amazon/stores/{store_id}/sync/inventory
  POST /api/v1/amazon/stores/{store_id}/sync/business-reports
  POST /api/v1/amazon/stores/{store_id}/sync/advertising
  ```

- [ ] 实现同步状态查询

  ```python
  GET /api/v1/amazon/sync-tasks?store_id={uuid}&status={status}
  GET /api/v1/amazon/sync-tasks/{task_id}
  ```

- [ ] 实现任务重试

  ```python
  POST /api/v1/amazon/sync-tasks/{task_id}/retry
  ```

- [ ] 编写 API 测试

**验收标准**:

- [ ] API 端点正常工作
- [ ] 权限验证正确
- [ ] API 测试通过

**相关文件**:

- `backend/app/api/v1/endpoints/amazon_sync.py` (新建)
- `backend/tests/api/test_amazon_sync.py` (新建)

---

#### Task 4.3: 前端同步界面 ⏱️ 4h

**描述**: 创建前端同步状态界面

**子任务**:

- [ ] 创建同步状态组件
  - 文件: `frontend/src/views/ads-analysis/components/SyncStatus.vue`
  - 显示最近同步时间
  - 显示同步状态 (成功/失败)
  - 显示同步记录数
- [ ] 添加手动同步按钮
  - 点击触发同步
  - 显示同步进度
  - 同步完成提示
- [ ] 添加同步历史列表
  - 表格显示历史记录
  - 支持筛选和排序
  - 显示错误详情
- [ ] 集成到主页面
  - 在广告分析页面顶部显示

**验收标准**:

- [ ] 可以查看同步状态
- [ ] 可以手动触发同步
- [ ] 可以查看同步历史

**相关文件**:

- `frontend/src/views/ads-analysis/components/SyncStatus.vue` (新建)
- `frontend/src/views/ads-analysis/index.vue` (修改)

---

### Phase 5: 测试和文档 (Day 7)

#### Task 5.1: 集成测试 ⏱️ 2h

**描述**: 端到端集成测试

**子任务**:

- [ ] 编写集成测试脚本
  - 文件: `backend/tests/integration/test_sync_workflow.py`
- [ ] 测试完整同步流程
  - 库存 → 业务 → 广告
- [ ] 测试数据一致性
- [ ] 测试并发场景

**验收标准**:

- [ ] 集成测试通过
- [ ] 数据一致性验证通过

---

#### Task 5.2: 性能测试 ⏱️ 2h

**描述**: 性能基准测试

**子任务**:

- [ ] 测试 1000 SKU 同步时间
- [ ] 测试并发同步性能
- [ ] 测试数据库查询性能
- [ ] 优化性能瓶颈

**验收标准**:

- [ ] 1000 SKU 同步 < 5 分钟
- [ ] 支持 10+ 店铺并发同步

---

#### Task 5.3: 文档完善 ⏱️ 2h

**描述**: 完善技术文档

**子任务**:

- [ ] 更新 API 文档
  - Swagger/OpenAPI 规范
- [ ] 编写部署文档
  - Celery 部署步骤
  - Redis 配置说明
- [ ] 编写运维文档
  - 监控指标
  - 故障排查
- [ ] 更新用户手册
  - 如何配置 Amazon API
  - 如何触发同步

**验收标准**:

- [ ] 文档完整清晰
- [ ] 可以按文档部署

**相关文件**:

- `docs/api/amazon-sync.md` (新建)
- `docs/deployment/celery-setup.md` (新建)
- `docs/user-guide/amazon-sync.md` (新建)

---

## 📊 进度追踪

### Day 1 (2026-01-02)

- [ ] Task 1.1: Celery 环境配置
- [ ] Task 1.2: 数据库表设计

### Day 2 (2026-01-03)

- [ ] Task 1.3: Amazon API 客户端基类

### Day 3 (2026-01-06)

- [ ] Task 2.1: SP-API 客户端实现

### Day 4 (2026-01-07)

- [ ] Task 2.2: 库存数据同步服务
- [ ] Task 2.3: 业务报告同步服务

### Day 5 (2026-01-08)

- [ ] Task 3.1: Advertising API 客户端

### Day 6 (2026-01-09)

- [ ] Task 3.2: 广告数据同步服务
- [ ] Task 4.1: Celery 任务定义

### Day 7 (2026-01-10)

- [ ] Task 4.2: REST API 端点
- [ ] Task 4.3: 前端同步界面
- [ ] Task 5.1: 集成测试
- [ ] Task 5.2: 性能测试
- [ ] Task 5.3: 文档完善

---

## ✅ 验收检查清单

### 功能验收

- [ ] 库存数据同步成功率 > 95%
- [ ] 业务报告同步成功率 > 95%
- [ ] 广告数据同步成功率 > 95%
- [ ] 定时任务准时触发率 > 99%
- [ ] 数据准确性 100%

### 性能验收

- [ ] 1000 SKU 库存同步 < 5 分钟
- [ ] 30 天业务报告同步 < 10 分钟
- [ ] 30 天广告数据同步 < 15 分钟
- [ ] 支持 10+ 店铺并发同步

### 质量验收

- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 代码审查通过
- [ ] 文档完整

---

## 🐛 风险和依赖

### 风险

1. **Amazon API 限流**: 需要实现请求限流和重试
2. **数据量大**: 需要优化批量插入性能
3. **网络不稳定**: 需要完善的错误处理和重试机制

### 依赖

1. **Amazon API 凭证**: 需要用户提供有效的 API 凭证
2. **Redis 服务**: Celery 依赖 Redis
3. **数据库性能**: 需要足够的数据库性能支持

---

**创建日期**: 2025-12-31  
**最后更新**: 2025-12-31  
**状态**: 待开始
