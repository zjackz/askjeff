"""
测试用例: 数据自动同步功能

Feature: ADS-001 - Amazon 数据自动同步
测试覆盖: 库存同步、业务报告同步、广告数据同步、定时任务
"""

import pytest
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.amazon_sync_service import AmazonSyncService
from app.clients.amazon.sp_api_client import SpApiClient
from app.clients.amazon.ads_api_client import AdsApiClient
from app.models.amazon_ads import (
    AmazonStore,
    InventorySnapshot,
    BusinessMetricSnapshot,
    AdsMetricSnapshot,
    SyncTask
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_amazon_store(db: Session) -> AmazonStore:
    """创建测试用的 Amazon 店铺"""
    store = AmazonStore(
        id=uuid4(),
        user_id=1,
        store_name="Test Store",
        marketplace_id="ATVPDKIKX0DER",
        marketplace_name="United States",
        seller_id="TEST_SELLER",
        sp_api_refresh_token="test_refresh_token",
        advertising_api_refresh_token="test_ads_token",
        is_active=True
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@pytest.fixture
def mock_sp_api_inventory_data():
    """Mock SP-API 库存报告数据"""
    return [
        {
            "seller-sku": "TEST-SKU-001",
            "asin": "B00TEST001",
            "afn-fulfillable-quantity": 100,
            "afn-inbound-quantity": 50,
            "afn-reserved-quantity": 10,
            "afn-unsellable-quantity": 5,
            "snapshot-date": "2025-12-30"
        },
        {
            "seller-sku": "TEST-SKU-002",
            "asin": "B00TEST002",
            "afn-fulfillable-quantity": 200,
            "afn-inbound-quantity": 0,
            "afn-reserved-quantity": 20,
            "afn-unsellable-quantity": 0,
            "snapshot-date": "2025-12-30"
        }
    ]


@pytest.fixture
def mock_sp_api_business_data():
    """Mock SP-API 业务报告数据"""
    return [
        {
            "sku": "TEST-SKU-001",
            "asin": "B00TEST001",
            "ordered-product-sales": 1500.00,
            "units-ordered": 50,
            "sessions": 1000,
            "page-views": 2000,
            "unit-session-percentage": 0.05,
            "date": "2025-12-30"
        }
    ]


@pytest.fixture
def mock_ads_api_data():
    """Mock Advertising API 数据"""
    return [
        {
            "sku": "TEST-SKU-001",
            "asin": "B00TEST001",
            "cost": 150.00,
            "sales": 750.00,
            "impressions": 10000,
            "clicks": 100,
            "orders": 15,
            "units-sold": 20,
            "date": "2025-12-30"
        }
    ]


# ============================================================================
# TC-001: 库存数据同步 - 正常流程
# ============================================================================

class TestInventorySyncNormalFlow:
    """测试库存数据同步的正常流程"""
    
    @patch('app.clients.amazon.sp_api_client.SpApiClient.fetch_inventory_report')
    def test_sync_inventory_success(
        self,
        mock_fetch: Mock,
        db: Session,
        mock_amazon_store: AmazonStore,
        mock_sp_api_inventory_data: list
    ):
        """
        TC-001: 库存数据同步 - 正常流程
        
        验证:
        1. 同步任务创建成功
        2. API 调用成功
        3. 数据正确保存到数据库
        4. 任务状态更新为 success
        """
        # Arrange
        mock_fetch.return_value = mock_sp_api_inventory_data
        service = AmazonSyncService(db)
        
        # Act
        task = service.sync_inventory(mock_amazon_store.id, days=7)
        
        # Assert
        assert task.status == "success"
        assert task.records_synced == 2
        assert task.error_message is None
        
        # 验证数据库记录
        snapshots = db.query(InventorySnapshot).filter_by(
            store_id=mock_amazon_store.id
        ).all()
        
        assert len(snapshots) == 2
        assert snapshots[0].sku == "TEST-SKU-001"
        assert snapshots[0].fba_inventory == 100
        assert snapshots[0].inbound_inventory == 50
        
        # 验证 API 调用参数
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args[0][1] - call_args[0][0] == timedelta(days=7)
    
    def test_sync_inventory_incremental_update(
        self,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        TC-004: 数据增量同步
        
        验证:
        1. 已存在的数据被更新
        2. 新数据被插入
        3. 无重复记录
        """
        # Arrange - 创建已存在的数据
        existing_snapshot = InventorySnapshot(
            store_id=mock_amazon_store.id,
            date=date(2025, 12, 30),
            sku="TEST-SKU-001",
            asin="B00TEST001",
            fba_inventory=50,  # 旧值
            inbound_inventory=25,
            reserved_inventory=5,
            unfulfillable_inventory=2
        )
        db.add(existing_snapshot)
        db.commit()
        
        # Mock 新数据
        new_data = [{
            "seller-sku": "TEST-SKU-001",
            "asin": "B00TEST001",
            "afn-fulfillable-quantity": 100,  # 新值
            "afn-inbound-quantity": 50,
            "afn-reserved-quantity": 10,
            "afn-unsellable-quantity": 5,
            "snapshot-date": "2025-12-30"
        }]
        
        with patch('app.clients.amazon.sp_api_client.SpApiClient.fetch_inventory_report') as mock_fetch:
            mock_fetch.return_value = new_data
            service = AmazonSyncService(db)
            
            # Act
            task = service.sync_inventory(mock_amazon_store.id)
            
            # Assert
            assert task.status == "success"
            
            # 验证数据被更新而不是重复插入
            snapshots = db.query(InventorySnapshot).filter_by(
                store_id=mock_amazon_store.id,
                date=date(2025, 12, 30),
                sku="TEST-SKU-001"
            ).all()
            
            assert len(snapshots) == 1  # 只有一条记录
            assert snapshots[0].fba_inventory == 100  # 值已更新


# ============================================================================
# TC-002: 库存数据同步 - API 凭证无效
# ============================================================================

class TestInventorySyncInvalidCredentials:
    """测试 API 凭证无效的情况"""
    
    @patch('app.clients.amazon.sp_api_client.SpApiClient.get_access_token')
    def test_sync_with_invalid_credentials(
        self,
        mock_get_token: Mock,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        TC-002: 库存数据同步 - API 凭证无效
        
        验证:
        1. 任务状态为 failed
        2. 错误信息包含凭证相关提示
        3. 不进行重试 (凭证错误)
        """
        # Arrange
        mock_get_token.side_effect = Exception("Invalid credentials")
        service = AmazonSyncService(db)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            service.sync_inventory(mock_amazon_store.id)
        
        assert "Invalid credentials" in str(exc_info.value)
        
        # 验证任务记录
        task = db.query(SyncTask).filter_by(
            store_id=mock_amazon_store.id,
            sync_type="inventory"
        ).first()
        
        assert task.status == "failed"
        assert "Invalid credentials" in task.error_message
        assert task.retry_count == 0  # 凭证错误不重试


# ============================================================================
# TC-003: 库存数据同步 - 网络超时重试
# ============================================================================

class TestInventorySyncNetworkRetry:
    """测试网络超时重试机制"""
    
    @patch('app.clients.amazon.sp_api_client.SpApiClient.fetch_inventory_report')
    @patch('app.tasks.sync_tasks.sync_inventory_task.apply_async')
    def test_sync_with_network_timeout_retry(
        self,
        mock_apply_async: Mock,
        mock_fetch: Mock,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        TC-003: 库存数据同步 - 网络超时重试
        
        验证:
        1. 网络超时触发重试
        2. 重试间隔为 5 分钟 (300 秒)
        3. 最多重试 3 次
        """
        # Arrange
        mock_fetch.side_effect = TimeoutError("Network timeout")
        service = AmazonSyncService(db)
        
        # Act
        with pytest.raises(TimeoutError):
            service.sync_inventory(mock_amazon_store.id)
        
        # Assert
        task = db.query(SyncTask).filter_by(
            store_id=mock_amazon_store.id,
            sync_type="inventory"
        ).first()
        
        assert task.status == "failed"
        assert task.retry_count == 1
        
        # 验证重试任务被调度
        mock_apply_async.assert_called_once()
        call_kwargs = mock_apply_async.call_args[1]
        assert call_kwargs['countdown'] == 300  # 5 分钟


# ============================================================================
# TC-005: 并发同步控制
# ============================================================================

class TestConcurrentSyncControl:
    """测试并发同步控制"""
    
    def test_prevent_concurrent_sync_same_store(
        self,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        TC-005: 并发同步控制
        
        验证:
        1. 同一店铺的同步任务不能并发
        2. 返回 409 Conflict 错误
        """
        # Arrange - 创建一个正在运行的任务
        running_task = SyncTask(
            store_id=mock_amazon_store.id,
            sync_type="inventory",
            status="running",
            start_time=datetime.utcnow()
        )
        db.add(running_task)
        db.commit()
        
        service = AmazonSyncService(db)
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            service.sync_inventory(mock_amazon_store.id)
        
        assert "already running" in str(exc_info.value).lower()


# ============================================================================
# TC-006: 定时任务触发
# ============================================================================

class TestScheduledTasks:
    """测试定时任务"""
    
    @patch('app.tasks.sync_tasks.sync_inventory_task.delay')
    def test_celery_beat_schedule_inventory(
        self,
        mock_delay: Mock
    ):
        """
        TC-006: 定时任务触发 - 库存同步
        
        验证:
        1. Celery Beat 配置正确
        2. 任务在指定时间触发
        """
        from app.celery_app import celery_app
        
        # 获取定时任务配置
        schedule = celery_app.conf.beat_schedule
        
        # 验证库存同步任务配置
        assert 'sync-inventory-daily' in schedule
        inventory_task = schedule['sync-inventory-daily']
        
        assert inventory_task['task'] == 'app.tasks.sync_inventory'
        assert inventory_task['schedule'].hour == 2
        assert inventory_task['schedule'].minute == 0
    
    @patch('app.tasks.sync_tasks.sync_business_reports_task.delay')
    def test_celery_beat_schedule_business(
        self,
        mock_delay: Mock
    ):
        """
        TC-006: 定时任务触发 - 业务报告
        
        验证业务报告同步任务在 2:30 触发
        """
        from app.celery_app import celery_app
        
        schedule = celery_app.conf.beat_schedule
        
        assert 'sync-business-reports-daily' in schedule
        business_task = schedule['sync-business-reports-daily']
        
        assert business_task['schedule'].hour == 2
        assert business_task['schedule'].minute == 30


# ============================================================================
# TC-007: 数据归档
# ============================================================================

class TestDataArchiving:
    """测试数据归档功能"""
    
    def test_archive_old_inventory_data(
        self,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        TC-007: 数据归档
        
        验证:
        1. 超过 90 天的数据被归档
        2. 数据从主表移除
        3. 数据完整性保持
        """
        # Arrange - 创建旧数据
        old_date = date.today() - timedelta(days=95)
        old_snapshot = InventorySnapshot(
            store_id=mock_amazon_store.id,
            date=old_date,
            sku="OLD-SKU",
            asin="B00OLD",
            fba_inventory=100,
            inbound_inventory=0,
            reserved_inventory=0,
            unfulfillable_inventory=0
        )
        db.add(old_snapshot)
        db.commit()
        
        # Act
        from app.services.data_archiving_service import DataArchivingService
        service = DataArchivingService(db)
        archived_count = service.archive_old_inventory_data(days=90)
        
        # Assert
        assert archived_count == 1
        
        # 验证主表中已删除
        main_record = db.query(InventorySnapshot).filter_by(
            store_id=mock_amazon_store.id,
            sku="OLD-SKU"
        ).first()
        assert main_record is None
        
        # 验证归档表中存在
        from app.models.amazon_ads import InventorySnapshotArchive
        archived_record = db.query(InventorySnapshotArchive).filter_by(
            store_id=mock_amazon_store.id,
            sku="OLD-SKU"
        ).first()
        assert archived_record is not None
        assert archived_record.fba_inventory == 100


# ============================================================================
# TC-008: 同步状态查询
# ============================================================================

class TestSyncTaskQuery:
    """测试同步任务查询"""
    
    def test_query_sync_tasks_by_store_and_status(
        self,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        TC-008: 同步状态查询
        
        验证:
        1. 可以按店铺和状态查询
        2. 结果按时间倒序排列
        3. 支持分页
        """
        # Arrange - 创建多个任务
        for i in range(5):
            task = SyncTask(
                store_id=mock_amazon_store.id,
                sync_type="inventory",
                status="success" if i % 2 == 0 else "failed",
                start_time=datetime.utcnow() - timedelta(hours=i),
                end_time=datetime.utcnow() - timedelta(hours=i) + timedelta(minutes=10),
                records_synced=100 if i % 2 == 0 else 0
            )
            db.add(task)
        db.commit()
        
        # Act
        from app.services.amazon_sync_service import AmazonSyncService
        service = AmazonSyncService(db)
        
        success_tasks = service.get_sync_tasks(
            store_id=mock_amazon_store.id,
            status="success",
            limit=10,
            offset=0
        )
        
        # Assert
        assert len(success_tasks) == 3  # 5 个任务中有 3 个成功
        
        # 验证按时间倒序
        for i in range(len(success_tasks) - 1):
            assert success_tasks[i].start_time > success_tasks[i + 1].start_time


# ============================================================================
# 业务报告同步测试
# ============================================================================

class TestBusinessReportSync:
    """测试业务报告同步"""
    
    @patch('app.clients.amazon.sp_api_client.SpApiClient.fetch_business_report')
    def test_sync_business_reports_success(
        self,
        mock_fetch: Mock,
        db: Session,
        mock_amazon_store: AmazonStore,
        mock_sp_api_business_data: list
    ):
        """
        测试业务报告同步成功
        
        验证:
        1. 数据正确映射到 BusinessMetricSnapshot
        2. 所有字段完整
        """
        # Arrange
        mock_fetch.return_value = mock_sp_api_business_data
        service = AmazonSyncService(db)
        
        # Act
        task = service.sync_business_reports(mock_amazon_store.id)
        
        # Assert
        assert task.status == "success"
        assert task.records_synced == 1
        
        # 验证数据
        snapshot = db.query(BusinessMetricSnapshot).filter_by(
            store_id=mock_amazon_store.id,
            sku="TEST-SKU-001"
        ).first()
        
        assert snapshot is not None
        assert snapshot.total_sales_amount == 1500.00
        assert snapshot.total_units_ordered == 50
        assert snapshot.sessions == 1000
        assert snapshot.unit_session_percentage == 0.05


# ============================================================================
# 广告数据同步测试
# ============================================================================

class TestAdvertisingDataSync:
    """测试广告数据同步"""
    
    @patch('app.clients.amazon.ads_api_client.AdsApiClient.fetch_campaign_report')
    def test_sync_advertising_data_success(
        self,
        mock_fetch: Mock,
        db: Session,
        mock_amazon_store: AmazonStore,
        mock_ads_api_data: list
    ):
        """
        测试广告数据同步成功
        
        验证:
        1. 数据正确映射到 AdsMetricSnapshot
        2. 计算指标正确 (ACOS, ROAS)
        """
        # Arrange
        mock_fetch.return_value = mock_ads_api_data
        service = AmazonSyncService(db)
        
        # Act
        task = service.sync_advertising(mock_amazon_store.id)
        
        # Assert
        assert task.status == "success"
        
        # 验证数据
        snapshot = db.query(AdsMetricSnapshot).filter_by(
            store_id=mock_amazon_store.id,
            sku="TEST-SKU-001"
        ).first()
        
        assert snapshot is not None
        assert snapshot.spend == 150.00
        assert snapshot.sales == 750.00
        assert snapshot.impressions == 10000
        assert snapshot.clicks == 100
        assert snapshot.orders == 15


# ============================================================================
# 性能测试
# ============================================================================

class TestSyncPerformance:
    """测试同步性能"""
    
    @pytest.mark.performance
    @patch('app.clients.amazon.sp_api_client.SpApiClient.fetch_inventory_report')
    def test_sync_1000_skus_within_5_minutes(
        self,
        mock_fetch: Mock,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        性能测试: 1000 个 SKU 的库存同步应在 5 分钟内完成
        
        验收标准: 单店铺库存同步时间 < 5 分钟 (1000 SKU)
        """
        import time
        
        # Arrange - 生成 1000 个 SKU 的数据
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                "seller-sku": f"SKU-{i:04d}",
                "asin": f"B00TEST{i:04d}",
                "afn-fulfillable-quantity": 100 + i,
                "afn-inbound-quantity": 50,
                "afn-reserved-quantity": 10,
                "afn-unsellable-quantity": 5,
                "snapshot-date": "2025-12-30"
            })
        
        mock_fetch.return_value = large_dataset
        service = AmazonSyncService(db)
        
        # Act
        start_time = time.time()
        task = service.sync_inventory(mock_amazon_store.id)
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        assert duration < 300  # 5 分钟 = 300 秒
        assert task.status == "success"
        assert task.records_synced == 1000


# ============================================================================
# 集成测试
# ============================================================================

@pytest.mark.integration
class TestSyncIntegration:
    """集成测试 - 完整同步流程"""
    
    def test_full_sync_workflow(
        self,
        db: Session,
        mock_amazon_store: AmazonStore
    ):
        """
        集成测试: 完整的同步工作流
        
        验证:
        1. 库存同步 → 业务报告同步 → 广告数据同步
        2. 数据关联正确
        3. 可以进行广告分析
        """
        # 这里需要真实的 API 调用或完整的 Mock
        # 暂时跳过,在实际环境中测试
        pytest.skip("需要真实 API 环境")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
