"""
Amazon 数据同步 Celery 任务

定义异步任务用于定时同步 Amazon 数据
"""

from celery import shared_task
from uuid import UUID

from app.db import SessionLocal
from app.services.amazon_sync_service import AmazonSyncService
from app.models.amazon_ads import AmazonStore


@shared_task(bind=True, max_retries=3)
def sync_inventory_task(self, store_id: str = None, days: int = 30, use_mock: bool = True):
    """
    同步库存数据任务
    
    Args:
        store_id: 店铺 ID (可选,None 表示同步所有店铺)
        days: 同步天数
        use_mock: 是否使用 Mock 数据
    
    Returns:
        dict: 同步结果
    """
    db = SessionLocal()
    try:
        service = AmazonSyncService(db)
        
        # 如果没有指定店铺,同步所有激活的店铺
        if store_id is None:
            stores = db.query(AmazonStore).filter_by(is_active=True).all()
            results = []
            for store in stores:
                try:
                    task = service.sync_inventory(store.id, days, use_mock)
                    results.append({
                        'store_id': str(store.id),
                        'store_name': store.store_name,
                        'status': task.status,
                        'records_synced': task.records_synced
                    })
                except Exception as e:
                    results.append({
                        'store_id': str(store.id),
                        'store_name': store.store_name,
                        'status': 'failed',
                        'error': str(e)
                    })
            return {'total_stores': len(stores), 'results': results}
        else:
            # 同步指定店铺
            task = service.sync_inventory(UUID(store_id), days, use_mock)
            return {
                'store_id': store_id,
                'status': task.status,
                'records_synced': task.records_synced
            }
    except Exception as exc:
        # 重试
        raise self.retry(exc=exc, countdown=300)  # 5 分钟后重试
    finally:
        db.close()


@shared_task(bind=True, max_retries=3)
def sync_business_reports_task(self, store_id: str = None, days: int = 30, use_mock: bool = True):
    """
    同步业务报告任务
    
    Args:
        store_id: 店铺 ID
        days: 同步天数
        use_mock: 是否使用 Mock 数据
    
    Returns:
        dict: 同步结果
    """
    db = SessionLocal()
    try:
        service = AmazonSyncService(db)
        
        if store_id is None:
            stores = db.query(AmazonStore).filter_by(is_active=True).all()
            results = []
            for store in stores:
                try:
                    task = service.sync_business_reports(store.id, days, use_mock)
                    results.append({
                        'store_id': str(store.id),
                        'store_name': store.store_name,
                        'status': task.status,
                        'records_synced': task.records_synced
                    })
                except Exception as e:
                    results.append({
                        'store_id': str(store.id),
                        'store_name': store.store_name,
                        'status': 'failed',
                        'error': str(e)
                    })
            return {'total_stores': len(stores), 'results': results}
        else:
            task = service.sync_business_reports(UUID(store_id), days, use_mock)
            return {
                'store_id': store_id,
                'status': task.status,
                'records_synced': task.records_synced
            }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()


@shared_task(bind=True, max_retries=3)
def sync_advertising_task(self, store_id: str = None, days: int = 30, use_mock: bool = True):
    """
    同步广告数据任务
    
    Args:
        store_id: 店铺 ID
        days: 同步天数
        use_mock: 是否使用 Mock 数据
    
    Returns:
        dict: 同步结果
    """
    db = SessionLocal()
    try:
        service = AmazonSyncService(db)
        
        if store_id is None:
            stores = db.query(AmazonStore).filter_by(is_active=True).all()
            results = []
            for store in stores:
                try:
                    task = service.sync_advertising(store.id, days, use_mock)
                    results.append({
                        'store_id': str(store.id),
                        'store_name': store.store_name,
                        'status': task.status,
                        'records_synced': task.records_synced
                    })
                except Exception as e:
                    results.append({
                        'store_id': str(store.id),
                        'store_name': store.store_name,
                        'status': 'failed',
                        'error': str(e)
                    })
            return {'total_stores': len(stores), 'results': results}
        else:
            task = service.sync_advertising(UUID(store_id), days, use_mock)
            return {
                'store_id': store_id,
                'status': task.status,
                'records_synced': task.records_synced
            }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()


@shared_task
def sync_all_stores_task(days: int = 30, use_mock: bool = True):
    """
    同步所有店铺的所有数据
    
    按顺序执行: 库存 → 业务 → 广告
    
    Args:
        days: 同步天数
        use_mock: 是否使用 Mock 数据
    
    Returns:
        dict: 同步结果汇总
    """
    results = {
        'inventory': sync_inventory_task.delay(days=days, use_mock=use_mock),
        'business': sync_business_reports_task.delay(days=days, use_mock=use_mock),
        'advertising': sync_advertising_task.delay(days=days, use_mock=use_mock),
    }
    
    return {
        'message': 'All sync tasks queued',
        'task_ids': {
            'inventory': results['inventory'].id,
            'business': results['business'].id,
            'advertising': results['advertising'].id,
        }
    }
