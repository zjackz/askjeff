# Feature 001: Phase 2 Assessment (已归档)

## Feature 001: Phase 2 Assessment (已归档)

> **注意**：本阶段的开发重心已从“通用广告管理 UI”转移至 **“智能广告诊断 (Smart Ads Diagnosis)”**。
> 请参考最新文档：[Smart Ads Diagnosis](./feature-002-smart-ads-diagnosis.md)
>
> 原有的 Campaign Manager 功能保留作为底层数据查看器，但不再作为核心交互界面。

## Feature 001 开发总结 - Phase 2 评估

**日期**: 2025-12-31 10:40  
**状态**: 暂停 / 转型

---

## 1. 当前进展概览

我们已经完成了广告管理模块的基础设施建设，包括：

1. **后端数据模型**: 建立了完整的 `AdvertisingCampaign`, `AdvertisingAdGroup` 及其性能快照模型。
2. **数据生成**: `seed_rich_data.py` 可以生成逼真的广告结构和性能数据。
3. **API 接口**: 实现了 `/api/v1/amazon/campaigns`，支持分页、排序、搜索和聚合统计。
4. **前端界面**: 开发了 `CampaignManager.vue`，实现了类似领星 ERP 的高密度数据表格。

## 2. 遇到的问题与反思

在开发过程中，我们意识到完全复刻 ERP 的“管理”功能可能偏离了 AskJeff 的核心价值。

### 2.1 核心冲突

* **ERP 模式**: 侧重于“全”，展示所有数据，提供所有操作（新建、编辑、批量调整）。用户需要自己去发现问题。
* **AskJeff 模式**: 侧重于“智”，直接告诉用户哪里有问题（如：无效花费、ACOS 过高）。

### 2.2 用户反馈 (模拟)
>
> "我不需要另一个表格来列出我的 500 个广告活动，我已经有亚马逊后台和领星了。我需要你告诉我，哪 5 个广告在浪费我的钱。"

## 3. 转型计划 (Pivot)

我们将停止开发复杂的“管理”功能（如行内编辑、批量操作），转而利用已有的数据基础，开发 **“智能诊断”** 模块。

### 3.1 新的目标

* **诊断优先**: 首页即展示“无效花费拦截”、“预算不足预警”等卡片。
* **一键优化**: 针对诊断出的问题，提供“一键暂停”、“一键加预算”的快捷操作。

### 3.2 保留价值

目前的 `CampaignManager` 不会白费，它将作为“查看详情”的底层视图。当用户点击诊断卡片时，可以跳转到过滤后的 `CampaignManager` 视图查看具体数据。

---

## 4. 技术债务记录

### 4.1 待修复

* `CampaignManager.vue` 中的 TypeScript 类型定义需要完善。
* 前端 API 调用目前硬编码了 `store_id`，需要对接全局 Store Context。

### 4.2 代码片段备份

以下是之前实现的 Campaign 列表查询逻辑，供参考：

```python
# backend/app/api/v1/endpoints/amazon_ads.py

@router.get("/campaigns", response_model=CampaignListResponse)
def get_campaigns(
    # ... params
):
    query = db.query(
        AdvertisingCampaign,
        func.sum(CampaignPerformanceSnapshot.impressions).label("total_impressions"),
        # ...
    )
    # ...
```

### 4.3 废弃设计

**原定 UI 布局**:

* 顶部：新建广告按钮、批量操作栏
* 中间：复杂的筛选器（状态、类型、ACOS 范围）
* 底部：分页数据表格

**新 UI 布局 (ActionsView)**:

* Grid 布局的诊断卡片
* 每个卡片包含：问题描述、影响金额、一键解决按钮

---

## 📊 当前状态

### ✅ Phase 1: 基础设施搭建 (100%)

**已完成**:

* ✅ Celery 环境配置
* ✅ 数据库表设计 (sync_tasks)
* ✅ Amazon API 客户端基类

**成果**:

* 4 个新文件
* 4 个修改文件
* 3 个 Docker 服务
* 1 个数据库表

**耗时**: 50 分钟 (预计 10 小时)

---

### 🔍 Phase 2: SP-API 集成 (评估)

#### 发现的现有实现

**已存在的文件**:

1. ✅ `app/clients/amazon/base_client.py` - Amazon API 基类
2. ✅ `app/clients/amazon/sp_api_client.py` - SP-API 客户端

**现有功能**:

```python
class SpApiClient(AmazonBaseClient):
    - get_inventory_summary(): 获取库存摘要
    - create_report(): 创建报告
    - get_report_document(): 获取报告文档
    - get_product_fees_estimate(): 获取费用预估
```

**评估结论**:

* ✅ 基础 SP-API 客户端已实现
* ⚠️ 缺少完整的报告生命周期管理
* ⚠️ 缺少数据解析和转换逻辑
* ⚠️ 缺少同步服务层

---

## 💡 建议的开发策略

### 选项 1: 完善现有实现 (推荐)

**目标**: 在现有基础上完善功能

**任务**:

1. 扩展 `SpApiClient`:
   * 添加 `fetch_inventory_report()` 方法
   * 添加 `fetch_business_report()` 方法
   * 添加报告等待和下载逻辑
   * 添加 CSV/JSON 解析器

2. 创建 `AmazonSyncService`:
   * 实现 `sync_inventory()` 方法
   * 实现 `sync_business_reports()` 方法
   * 实现任务状态管理
   * 实现错误处理和重试

3. 创建 Celery 任务:
   * `sync_inventory_task`
   * `sync_business_reports_task`
   * `sync_advertising_task`

**预计时间**: 8-10 小时

---

### 选项 2: 使用 Mock 数据快速验证 (快速)

**目标**: 先实现完整流程,后续再对接真实 API

**任务**:

1. 创建 Mock 数据生成器
2. 实现同步服务(使用 Mock 数据)
3. 实现 Celery 任务
4. 端到端测试

**优点**:

* 快速验证整体架构
* 不依赖 Amazon API 凭证
* 便于测试和调试

**预计时间**: 2-3 小时

---

### 选项 3: 分阶段实现 (平衡)

**阶段 1**: 核心服务框架 (1-2 小时)

* 创建 `AmazonSyncService` 骨架
* 创建 Celery 任务定义
* 实现基本的任务状态管理

**阶段 2**: Mock 数据验证 (1 小时)

* 使用 Mock 数据测试流程
* 验证数据保存逻辑
* 验证任务调度

**阶段 3**: 真实 API 集成 (4-6 小时)

* 完善 SP-API 客户端
* 实现报告下载和解析
* 处理 API 限流和错误

---

## 🎯 推荐方案

### 立即执行: 选项 2 (Mock 数据快速验证)

**理由**:

1. 快速验证整体架构设计
2. 不需要 Amazon API 凭证
3. 便于编写和运行测试
4. 为后续真实 API 集成打好基础

**实施步骤**:

#### Step 1: 创建 Mock 数据生成器 (30 分钟)

```python
# app/services/mock_data_generator.py
class MockDataGenerator:
    @staticmethod
    def generate_inventory_data(store_id, days=30):
        """生成 Mock 库存数据"""
        pass
    
    @staticmethod
    def generate_business_data(store_id, days=30):
        """生成 Mock 业务数据"""
        pass
```

#### Step 2: 创建同步服务 (1 小时)

```python
# app/services/amazon_sync_service.py
class AmazonSyncService:
    def sync_inventory(self, store_id, days=30):
        """同步库存数据"""
        # 1. 创建任务记录
        # 2. 获取数据 (Mock 或真实 API)
        # 3. 保存到数据库
        # 4. 更新任务状态
        pass
```

#### Step 3: 创建 Celery 任务 (30 分钟)

```python
# app/tasks/sync_tasks.py
@shared_task
def sync_inventory_task(store_id):
    service = AmazonSyncService(db)
    return service.sync_inventory(store_id)
```

#### Step 4: 端到端测试 (30 分钟)

* 手动触发同步任务
* 验证数据保存
* 验证任务状态
* 验证定时调度

---

## 📋 下一步行动

### 立即开始 (推荐)

**任务**: 实现 Mock 数据同步流程

**文件清单**:

1. `backend/app/services/mock_data_generator.py` (新建)
2. `backend/app/services/amazon_sync_service.py` (新建)
3. `backend/app/tasks/sync_tasks.py` (新建)
4. `backend/tests/test_sync_service.py` (新建)

**预计时间**: 2-3 小时

**验收标准**:

* [ ] 可以手动触发同步任务
* [ ] 数据正确保存到数据库
* [ ] 任务状态正确更新
* [ ] 定时任务可以自动触发

---

### 或者: 暂停并总结

**选择此选项如果**:

* 需要休息
* 需要审查当前代码
* 需要讨论技术方案

**已完成的工作**:

* ✅ Phase 1 基础设施 100%
* ✅ 3 次代码提交
* ✅ 完整的文档体系
* ✅ 规范的开发流程

---

## 📊 项目整体进度

```
Feature 001: 数据自动同步
├─ Phase 1: 基础设施搭建  ████████████████████ 100% ✅
├─ Phase 2: SP-API 集成    ░░░░░░░░░░░░░░░░░░░░   0%
├─ Phase 3: Ads API 集成   ░░░░░░░░░░░░░░░░░░░░   0%
├─ Phase 4: 定时任务和API  ░░░░░░░░░░░░░░░░░░░░   0%
└─ Phase 5: 测试和文档     ░░░░░░░░░░░░░░░░░░░░   0%

总进度: 23% (3/13 tasks)
```

---

## ✅ 总结

**当前成就**:

* ✅ Phase 1 完成 (50 分钟,超前 91%)
* ✅ 发现现有 SP-API 实现
* ✅ 评估了 3 种开发策略

**推荐行动**:

* 🎯 选项 2: Mock 数据快速验证
* ⏱️ 预计 2-3 小时完成
* 🎁 可快速验证整体架构

**等待指示**:

* 继续实现 Mock 数据方案?
* 或直接对接真实 API?
* 或暂停并休息?

---

**准备就绪,等待你的决定! 🚀**
