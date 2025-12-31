# Feature 001: 数据自动同步

**功能编号**: ADS-001  
**功能名称**: Amazon 数据自动同步  
**优先级**: P0 (核心功能)  
**负责人**: Backend Team  
**创建日期**: 2025-12-31  
**预计工作量**: 5-7 天

---

## 📋 需求概述

### 业务背景

当前系统使用 Mock 数据进行广告分析,无法反映真实的业务情况。需要实现与 Amazon API 的自动数据同步,确保分析基于最新、准确的数据。

### 目标用户

- 亚马逊卖家
- 运营团队
- 数据分析师

### 核心价值

1. **数据实时性**: 每日自动同步,确保数据新鲜度
2. **数据准确性**: 直接从 Amazon 官方 API 获取,避免人工录入错误
3. **运营效率**: 自动化替代人工导出导入,节省时间
4. **决策支持**: 基于真实数据的分析和建议

---

## 🎯 功能需求

### FR-001: SP-API 库存数据同步

**描述**: 自动同步 FBA 库存报告数据

**输入**:

- 店铺 ID (UUID)
- 同步日期范围 (可选,默认最近 30 天)

**输出**:

- 库存快照记录 (InventorySnapshot)
- 同步状态报告

**业务规则**:

1. 每日凌晨 2:00 自动触发同步
2. 同步最近 30 天的数据
3. 已存在的数据进行更新,新数据进行插入
4. 同步失败自动重试 3 次,间隔 5 分钟
5. 超过 90 天的数据自动归档

**数据映射**:

```python
# Amazon FBA Inventory Report → InventorySnapshot
{
    "sku": report["seller-sku"],
    "asin": report["asin"],
    "fba_inventory": report["afn-fulfillable-quantity"],
    "inbound_inventory": report["afn-inbound-quantity"],
    "reserved_inventory": report["afn-reserved-quantity"],
    "unfulfillable_inventory": report["afn-unsellable-quantity"],
    "date": report["snapshot-date"]
}
```

**API 端点**:

```
POST /api/v1/amazon/stores/{store_id}/sync/inventory
GET  /api/v1/amazon/stores/{store_id}/sync/inventory/status
```

---

### FR-002: SP-API 业务报告同步

**描述**: 自动同步业务报告数据 (销售额、订单量等)

**输入**:

- 店铺 ID (UUID)
- 报告类型 (GET_SALES_AND_TRAFFIC_REPORT)
- 同步日期范围

**输出**:

- 业务指标快照 (BusinessMetricSnapshot)
- 同步状态报告

**业务规则**:

1. 每日凌晨 2:30 自动触发
2. 同步最近 30 天的数据
3. 按 SKU 和日期聚合数据
4. 数据延迟处理: Amazon 数据有 48 小时延迟,同步时考虑此延迟

**数据映射**:

```python
# Amazon Business Report → BusinessMetricSnapshot
{
    "sku": report["sku"],
    "asin": report["asin"],
    "total_sales_amount": report["ordered-product-sales"],
    "total_units_ordered": report["units-ordered"],
    "sessions": report["sessions"],
    "page_views": report["page-views"],
    "unit_session_percentage": report["unit-session-percentage"],
    "date": report["date"]
}
```

**API 端点**:

```
POST /api/v1/amazon/stores/{store_id}/sync/business-reports
GET  /api/v1/amazon/stores/{store_id}/sync/business-reports/status
```

---

### FR-003: Advertising API 广告数据同步

**描述**: 自动同步广告表现数据

**输入**:

- 店铺 ID (UUID)
- 报告类型 (Campaign, Ad Group, Keyword, Search Term)
- 同步日期范围

**输出**:

- 广告指标快照 (AdsMetricSnapshot)
- 同步状态报告

**业务规则**:

1. 每日凌晨 3:00 自动触发
2. 同步最近 30 天的数据
3. 按 SKU 聚合 Campaign/Ad Group/Keyword 数据
4. 支持增量同步,避免重复拉取

**数据映射**:

```python
# Amazon Advertising Report → AdsMetricSnapshot
{
    "sku": extract_sku_from_campaign(report),
    "asin": report["asin"],
    "spend": report["cost"],
    "sales": report["sales"],
    "impressions": report["impressions"],
    "clicks": report["clicks"],
    "orders": report["orders"],
    "units": report["units-sold"],
    "date": report["date"]
}
```

**API 端点**:

```
POST /api/v1/amazon/stores/{store_id}/sync/advertising
GET  /api/v1/amazon/stores/{store_id}/sync/advertising/status
```

---

### FR-004: 同步任务调度

**描述**: 定时任务调度系统

**功能点**:

1. **定时触发**
   - 使用 APScheduler 或 Celery Beat
   - 支持 Cron 表达式配置
   - 支持手动触发

2. **任务队列**
   - 使用 Celery 异步任务队列
   - 支持任务优先级
   - 支持任务重试

3. **任务监控**
   - 任务执行状态追踪
   - 任务执行时长统计
   - 失败任务告警

**调度配置**:

```python
# 定时任务配置
CELERY_BEAT_SCHEDULE = {
    'sync-inventory-daily': {
        'task': 'app.tasks.sync_inventory',
        'schedule': crontab(hour=2, minute=0),  # 每日 2:00
    },
    'sync-business-reports-daily': {
        'task': 'app.tasks.sync_business_reports',
        'schedule': crontab(hour=2, minute=30),  # 每日 2:30
    },
    'sync-advertising-daily': {
        'task': 'app.tasks.sync_advertising',
        'schedule': crontab(hour=3, minute=0),  # 每日 3:00
    },
}
```

---

### FR-005: 同步状态管理

**描述**: 同步任务状态追踪和管理

**数据模型**:

```python
class SyncTask(Base):
    """同步任务记录"""
    id: UUID
    store_id: UUID
    sync_type: str  # inventory, business, advertising
    status: str  # pending, running, success, failed
    start_time: datetime
    end_time: datetime
    records_synced: int
    records_failed: int
    error_message: str
    retry_count: int
```

**状态流转**:

```
pending → running → success
                 → failed → pending (重试)
```

**API 端点**:

```
GET /api/v1/amazon/sync-tasks?store_id={uuid}&status={status}
GET /api/v1/amazon/sync-tasks/{task_id}
POST /api/v1/amazon/sync-tasks/{task_id}/retry
```

---

## 🔧 技术设计

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 同步状态面板  │  │ 手动触发按钮  │  │ 同步历史记录  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP API
┌─────────────────────────────────────────────────────────┐
│                   Backend API (FastAPI)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Sync Controller (REST Endpoints)         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Task Queue (Celery)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Inventory│  │ Business │  │   Ads    │             │
│  │   Task   │  │   Task   │  │   Task   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Amazon API Clients                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ SP-API   │  │ SP-API   │  │   Ads    │             │
│  │ Inventory│  │ Business │  │   API    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Amazon APIs                          │
│  • SP-API (Selling Partner API)                        │
│  • Advertising API                                     │
└─────────────────────────────────────────────────────────┘
```

---

### 核心类设计

#### 1. Amazon API 客户端基类

```python
# app/clients/amazon/base_client.py

from abc import ABC, abstractmethod
from typing import Dict, Any
import requests
from datetime import datetime, timedelta

class AmazonBaseClient(ABC):
    """Amazon API 客户端基类"""
    
    def __init__(self, store: AmazonStore):
        self.store = store
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self) -> str:
        """获取访问令牌 (自动刷新)"""
        if self.access_token and self.token_expires_at > datetime.utcnow():
            return self.access_token
        
        # 使用 refresh_token 获取新的 access_token
        response = requests.post(
            "https://api.amazon.com/auth/o2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.store.sp_api_refresh_token,
                "client_id": settings.amazon_client_id,
                "client_secret": settings.amazon_client_secret,
            }
        )
        
        data = response.json()
        self.access_token = data["access_token"]
        self.token_expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
        
        return self.access_token
    
    @abstractmethod
    def fetch_data(self, start_date: date, end_date: date) -> List[Dict]:
        """获取数据 (子类实现)"""
        pass
```

#### 2. SP-API 客户端

```python
# app/clients/amazon/sp_api_client.py

class SpApiClient(AmazonBaseClient):
    """SP-API 客户端"""
    
    def fetch_inventory_report(self, start_date: date, end_date: date) -> List[Dict]:
        """获取库存报告"""
        # 1. 创建报告请求
        report_id = self._create_report("GET_FBA_INVENTORY_AGED_DATA")
        
        # 2. 等待报告生成
        self._wait_for_report(report_id)
        
        # 3. 下载报告
        report_data = self._download_report(report_id)
        
        # 4. 解析报告
        return self._parse_inventory_report(report_data)
    
    def fetch_business_report(self, start_date: date, end_date: date) -> List[Dict]:
        """获取业务报告"""
        report_id = self._create_report(
            "GET_SALES_AND_TRAFFIC_REPORT",
            data_start_time=start_date,
            data_end_time=end_date
        )
        
        self._wait_for_report(report_id)
        report_data = self._download_report(report_id)
        
        return self._parse_business_report(report_data)
```

#### 3. Advertising API 客户端

```python
# app/clients/amazon/ads_api_client.py

class AdsApiClient(AmazonBaseClient):
    """Advertising API 客户端"""
    
    def fetch_campaign_report(self, start_date: date, end_date: date) -> List[Dict]:
        """获取 Campaign 报告"""
        # 1. 创建报告请求
        report_id = self._create_report({
            "reportDate": start_date.isoformat(),
            "metrics": "impressions,clicks,cost,sales,orders"
        })
        
        # 2. 轮询报告状态
        self._poll_report_status(report_id)
        
        # 3. 下载报告
        report_data = self._download_report(report_id)
        
        return self._parse_campaign_report(report_data)
```

#### 4. 同步服务

```python
# app/services/amazon_sync_service.py

class AmazonSyncService:
    """Amazon 数据同步服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def sync_inventory(self, store_id: UUID, days: int = 30) -> SyncTask:
        """同步库存数据"""
        # 1. 创建同步任务记录
        task = SyncTask(
            store_id=store_id,
            sync_type="inventory",
            status="running",
            start_time=datetime.utcnow()
        )
        self.db.add(task)
        self.db.commit()
        
        try:
            # 2. 获取店铺信息
            store = self.db.query(AmazonStore).filter_by(id=store_id).first()
            
            # 3. 初始化 API 客户端
            client = SpApiClient(store)
            
            # 4. 获取数据
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            inventory_data = client.fetch_inventory_report(start_date, end_date)
            
            # 5. 保存到数据库
            records_synced = 0
            for item in inventory_data:
                snapshot = InventorySnapshot(
                    store_id=store_id,
                    date=item["date"],
                    sku=item["sku"],
                    asin=item["asin"],
                    fba_inventory=item["fba_inventory"],
                    inbound_inventory=item["inbound_inventory"],
                    reserved_inventory=item["reserved_inventory"],
                    unfulfillable_inventory=item["unfulfillable_inventory"]
                )
                
                # Upsert 操作
                existing = self.db.query(InventorySnapshot).filter_by(
                    store_id=store_id,
                    date=item["date"],
                    sku=item["sku"]
                ).first()
                
                if existing:
                    for key, value in snapshot.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                else:
                    self.db.add(snapshot)
                
                records_synced += 1
            
            # 6. 更新任务状态
            task.status = "success"
            task.end_time = datetime.utcnow()
            task.records_synced = records_synced
            self.db.commit()
            
            return task
            
        except Exception as e:
            # 7. 错误处理
            task.status = "failed"
            task.end_time = datetime.utcnow()
            task.error_message = str(e)
            task.retry_count += 1
            self.db.commit()
            
            # 8. 重试逻辑
            if task.retry_count < 3:
                # 5 分钟后重试
                sync_inventory_task.apply_async(
                    args=[store_id, days],
                    countdown=300
                )
            
            raise
```

#### 5. Celery 任务

```python
# app/tasks/sync_tasks.py

from celery import shared_task

@shared_task(bind=True, max_retries=3)
def sync_inventory_task(self, store_id: str, days: int = 30):
    """库存同步任务"""
    db = SessionLocal()
    try:
        service = AmazonSyncService(db)
        return service.sync_inventory(UUID(store_id), days)
    except Exception as exc:
        # 重试
        raise self.retry(exc=exc, countdown=300)  # 5 分钟后重试
    finally:
        db.close()

@shared_task
def sync_business_reports_task(store_id: str, days: int = 30):
    """业务报告同步任务"""
    db = SessionLocal()
    try:
        service = AmazonSyncService(db)
        return service.sync_business_reports(UUID(store_id), days)
    finally:
        db.close()

@shared_task
def sync_advertising_task(store_id: str, days: int = 30):
    """广告数据同步任务"""
    db = SessionLocal()
    try:
        service = AmazonSyncService(db)
        return service.sync_advertising(UUID(store_id), days)
    finally:
        db.close()
```

---

### 数据库设计

#### 新增表: sync_tasks

```sql
CREATE TABLE sync_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES amazon_stores(id) ON DELETE CASCADE,
    sync_type VARCHAR(50) NOT NULL,  -- inventory, business, advertising
    status VARCHAR(20) NOT NULL,     -- pending, running, success, failed
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    records_synced INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_store_sync_type (store_id, sync_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

---

## 🧪 测试用例

### TC-001: 库存数据同步 - 正常流程

**前置条件**:

- 店铺已配置 SP-API 凭证
- 数据库连接正常
- Celery 服务运行中

**测试步骤**:

1. 调用 `POST /api/v1/amazon/stores/{store_id}/sync/inventory`
2. 验证返回 202 Accepted 和 task_id
3. 轮询 `GET /api/v1/amazon/sync-tasks/{task_id}` 直到状态为 success
4. 查询数据库验证 InventorySnapshot 记录已创建

**预期结果**:

- 同步任务状态为 success
- records_synced > 0
- 数据库中存在对应日期的库存快照
- 数据字段完整且准确

**测试数据**:

```json
{
  "store_id": "550e8400-e29b-41d4-a716-446655440000",
  "days": 7
}
```

---

### TC-002: 库存数据同步 - API 凭证无效

**前置条件**:

- 店铺 SP-API refresh_token 已过期或无效

**测试步骤**:

1. 调用同步 API
2. 等待任务完成

**预期结果**:

- 任务状态为 failed
- error_message 包含 "Invalid credentials" 或类似信息
- retry_count = 0 (凭证错误不重试)

---

### TC-003: 库存数据同步 - 网络超时重试

**前置条件**:

- 模拟网络超时 (使用 Mock)

**测试步骤**:

1. Mock Amazon API 返回超时
2. 调用同步 API
3. 观察重试行为

**预期结果**:

- 任务自动重试 3 次
- 每次重试间隔 5 分钟
- 3 次失败后状态为 failed
- retry_count = 3

---

### TC-004: 数据增量同步

**前置条件**:

- 数据库中已存在部分库存数据

**测试步骤**:

1. 记录现有数据的 SKU 列表
2. 调用同步 API
3. 验证数据更新和新增

**预期结果**:

- 已存在的 SKU 数据被更新 (updated_at 字段变化)
- 新 SKU 数据被插入
- 无重复记录

---

### TC-005: 并发同步控制

**前置条件**:

- 同一店铺的同步任务正在运行

**测试步骤**:

1. 启动第一个同步任务
2. 立即启动第二个同步任务

**预期结果**:

- 第二个任务返回 409 Conflict
- 错误信息: "Sync task already running for this store"

---

### TC-006: 定时任务触发

**前置条件**:

- Celery Beat 服务运行中
- 配置了定时任务

**测试步骤**:

1. 等待定时任务触发时间 (或手动触发)
2. 检查 sync_tasks 表

**预期结果**:

- 每日 2:00 自动创建库存同步任务
- 每日 2:30 自动创建业务报告同步任务
- 每日 3:00 自动创建广告数据同步任务

---

### TC-007: 数据归档

**前置条件**:

- 数据库中存在超过 90 天的数据

**测试步骤**:

1. 运行归档任务
2. 检查主表和归档表

**预期结果**:

- 超过 90 天的数据从主表移除
- 数据存在于归档表中
- 数据完整性保持

---

### TC-008: 同步状态查询

**测试步骤**:

1. 调用 `GET /api/v1/amazon/sync-tasks?store_id={uuid}&status=success`
2. 验证返回结果

**预期结果**:

- 返回该店铺所有成功的同步任务
- 按时间倒序排列
- 包含分页信息

---

## 📊 验收标准

### 功能验收

- [ ] 库存数据同步成功率 > 95%
- [ ] 业务报告同步成功率 > 95%
- [ ] 广告数据同步成功率 > 95%
- [ ] 定时任务准时触发率 > 99%
- [ ] 数据准确性 100% (与 Amazon Seller Central 对比)

### 性能验收

- [ ] 单店铺库存同步时间 < 5 分钟 (1000 SKU)
- [ ] 单店铺业务报告同步时间 < 10 分钟 (30 天数据)
- [ ] 单店铺广告数据同步时间 < 15 分钟 (30 天数据)
- [ ] 并发同步支持 > 10 个店铺

### 可靠性验收

- [ ] 网络异常自动重试成功率 > 90%
- [ ] 系统异常恢复时间 < 10 分钟
- [ ] 数据一致性 100% (无重复、无丢失)

---

## 📝 实施计划

### Day 1-2: 基础设施搭建

- [ ] 安装配置 Celery 和 Redis
- [ ] 创建 Amazon API 客户端基类
- [ ] 设计数据库表结构
- [ ] 编写数据库迁移脚本

### Day 3-4: SP-API 集成

- [ ] 实现 SP-API 客户端
- [ ] 实现库存数据同步
- [ ] 实现业务报告同步
- [ ] 编写单元测试

### Day 5-6: Advertising API 集成

- [ ] 实现 Advertising API 客户端
- [ ] 实现广告数据同步
- [ ] 编写单元测试

### Day 7: 定时任务和测试

- [ ] 配置 Celery Beat 定时任务
- [ ] 集成测试
- [ ] 性能测试
- [ ] 文档完善

---

## 🔗 相关文档

- [Amazon SP-API 官方文档](https://developer-docs.amazon.com/sp-api/)
- [Amazon Advertising API 文档](https://advertising.amazon.com/API/docs)
- [Celery 官方文档](https://docs.celeryq.dev/)
- [数据库设计文档](./database-design.md)

---

**文档版本**: v1.0  
**最后更新**: 2025-12-31  
**审核状态**: 待审核
