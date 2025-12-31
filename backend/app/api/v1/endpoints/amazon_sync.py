"""
Amazon 数据同步 API 端点

提供手动触发同步任务和查询同步状态的接口
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.amazon_ads import AmazonStore, SyncTask
from app.tasks.sync_tasks import (
    sync_inventory_task,
    sync_business_reports_task,
    sync_advertising_task,
    sync_all_stores_task
)
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/stores/{store_id}/sync/inventory", summary="触发库存同步")
async def trigger_inventory_sync(
    store_id: UUID,
    days: int = Query(30, ge=1, le=90, description="同步天数"),
    use_mock: bool = Query(True, description="是否使用 Mock 数据"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    触发指定店铺的库存数据同步任务 (异步)
    """
    store = db.query(AmazonStore).filter(AmazonStore.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # 触发 Celery 任务
    task = sync_inventory_task.delay(store_id=str(store_id), days=days, use_mock=use_mock)
    
    return {
        "message": "Inventory sync task started",
        "task_id": task.id,
        "store_id": str(store_id)
    }


@router.post("/stores/{store_id}/sync/business", summary="触发业务报告同步")
async def trigger_business_sync(
    store_id: UUID,
    days: int = Query(30, ge=1, le=90, description="同步天数"),
    use_mock: bool = Query(True, description="是否使用 Mock 数据"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    触发指定店铺的业务报告同步任务 (异步)
    """
    store = db.query(AmazonStore).filter(AmazonStore.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    task = sync_business_reports_task.delay(store_id=str(store_id), days=days, use_mock=use_mock)
    
    return {
        "message": "Business report sync task started",
        "task_id": task.id,
        "store_id": str(store_id)
    }


@router.post("/stores/{store_id}/sync/ads", summary="触发广告数据同步")
async def trigger_ads_sync(
    store_id: UUID,
    days: int = Query(30, ge=1, le=90, description="同步天数"),
    use_mock: bool = Query(True, description="是否使用 Mock 数据"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    触发指定店铺的广告数据同步任务 (异步)
    """
    store = db.query(AmazonStore).filter(AmazonStore.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    task = sync_advertising_task.delay(store_id=str(store_id), days=days, use_mock=use_mock)
    
    return {
        "message": "Advertising sync task started",
        "task_id": task.id,
        "store_id": str(store_id)
    }


@router.post("/sync/all", summary="触发所有同步")
async def trigger_all_sync(
    days: int = Query(30, ge=1, le=90, description="同步天数"),
    use_mock: bool = Query(True, description="是否使用 Mock 数据"),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    触发所有店铺的所有数据同步任务 (异步)
    """
    result = sync_all_stores_task(days=days, use_mock=use_mock)
    
    return result


@router.get("/sync-tasks", summary="查询同步任务历史")
async def get_sync_tasks(
    store_id: Optional[UUID] = None,
    sync_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    查询同步任务历史记录
    """
    query = db.query(SyncTask)
    
    if store_id:
        query = query.filter(SyncTask.store_id == store_id)
    if sync_type:
        query = query.filter(SyncTask.sync_type == sync_type)
    if status:
        query = query.filter(SyncTask.status == status)
        
    # 按创建时间倒序
    query = query.order_by(SyncTask.created_at.desc())
    
    tasks = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(t.id),
            "store_id": str(t.store_id),
            "sync_type": t.sync_type,
            "status": t.status,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "records_synced": t.records_synced,
            "records_failed": t.records_failed,
            "error_message": t.error_message,
            "created_at": t.created_at
        }
        for t in tasks
    ]
