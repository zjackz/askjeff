"""
Amazon 店铺管理 API 端点

提供店铺的 CRUD 操作和凭证验证接口
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.amazon_ads import AmazonStore, SyncTask
from app.tasks.sync_tasks import sync_inventory_task

router = APIRouter()


class StoreCreate(BaseModel):
    """创建店铺请求"""
    store_name: str = Field(..., min_length=1, max_length=255, description="店铺名称")
    marketplace_id: str = Field(..., min_length=1, max_length=20, description="市场 ID")
    marketplace_name: str = Field(..., min_length=1, max_length=50, description="市场名称")
    seller_id: str = Field(..., min_length=1, max_length=50, description="卖家 ID")
    sp_api_refresh_token: Optional[str] = Field(None, description="SP API Refresh Token")
    advertising_api_refresh_token: Optional[str] = Field(None, description="Advertising API Refresh Token")
    is_active: bool = Field(True, description="是否启用")


class StoreUpdate(BaseModel):
    """更新店铺请求"""
    store_name: Optional[str] = Field(None, min_length=1, max_length=255)
    sp_api_refresh_token: Optional[str] = None
    advertising_api_refresh_token: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(BaseModel):
    """店铺响应"""
    id: str
    user_id: int
    store_name: str
    marketplace_id: str
    marketplace_name: str
    seller_id: str
    is_active: bool
    last_sync_at: Optional[str]
    created_at: str
    updated_at: str


@router.get("", summary="获取店铺列表")
async def get_stores(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    marketplace_id: Optional[str] = Query(None, description="市场 ID"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前用户的店铺列表
    """
    query = db.query(AmazonStore).filter(AmazonStore.user_id == current_user["id"])

    # 筛选条件
    if is_active is not None:
        query = query.filter(AmazonStore.is_active == is_active)
    if marketplace_id:
        query = query.filter(AmazonStore.marketplace_id == marketplace_id)

    # 分页
    total = query.count()
    stores = query.order_by(AmazonStore.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(store.id),
                "user_id": store.user_id,
                "store_name": store.store_name,
                "marketplace_id": store.marketplace_id,
                "marketplace_name": store.marketplace_name,
                "seller_id": store.seller_id,
                "is_active": store.is_active,
                "last_sync_at": store.last_sync_at.isoformat() if store.last_sync_at else None,
                "created_at": store.created_at.isoformat(),
                "updated_at": store.updated_at.isoformat()
            }
            for store in stores
        ]
    }


@router.get("/{store_id}", summary="获取店铺详情")
async def get_store(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取指定店铺的详细信息
    """
    store = db.query(AmazonStore).filter(
        AmazonStore.id == store_id,
        AmazonStore.user_id == current_user["id"]
    ).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # 获取最近一次同步状态
    latest_sync = db.query(SyncTask).filter(
        SyncTask.store_id == store_id
    ).order_by(SyncTask.created_at.desc()).first()

    return {
        "id": str(store.id),
        "user_id": store.user_id,
        "store_name": store.store_name,
        "marketplace_id": store.marketplace_id,
        "marketplace_name": store.marketplace_name,
        "seller_id": store.seller_id,
        "is_active": store.is_active,
        "last_sync_at": store.last_sync_at.isoformat() if store.last_sync_at else None,
        "created_at": store.created_at.isoformat(),
        "updated_at": store.updated_at.isoformat(),
        "has_credentials": bool(store.sp_api_refresh_token or store.advertising_api_refresh_token),
        "latest_sync": {
            "status": latest_sync.status if latest_sync else "never",
            "sync_type": latest_sync.sync_type if latest_sync else None,
            "created_at": latest_sync.created_at.isoformat() if latest_sync else None
        } if latest_sync else None
    }


@router.post("", summary="创建店铺")
async def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    创建新店铺
    """
    # 检查是否已存在相同的店铺
    existing = db.query(AmazonStore).filter(
        AmazonStore.user_id == current_user["id"],
        AmazonStore.marketplace_id == store_data.marketplace_id,
        AmazonStore.seller_id == store_data.seller_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Store already exists")

    store = AmazonStore(
        user_id=current_user["id"],
        store_name=store_data.store_name,
        marketplace_id=store_data.marketplace_id,
        marketplace_name=store_data.marketplace_name,
        seller_id=store_data.seller_id,
        sp_api_refresh_token=store_data.sp_api_refresh_token,
        advertising_api_refresh_token=store_data.advertising_api_refresh_token,
        is_active=store_data.is_active
    )

    db.add(store)
    db.commit()
    db.refresh(store)

    return {
        "message": "Store created successfully",
        "id": str(store.id)
    }


@router.put("/{store_id}", summary="更新店铺")
async def update_store(
    store_id: UUID,
    store_data: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    更新店铺信息
    """
    store = db.query(AmazonStore).filter(
        AmazonStore.id == store_id,
        AmazonStore.user_id == current_user["id"]
    ).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # 更新字段
    if store_data.store_name is not None:
        store.store_name = store_data.store_name
    if store_data.sp_api_refresh_token is not None:
        store.sp_api_refresh_token = store_data.sp_api_refresh_token
    if store_data.advertising_api_refresh_token is not None:
        store.advertising_api_refresh_token = store_data.advertising_api_refresh_token
    if store_data.is_active is not None:
        store.is_active = store_data.is_active

    db.commit()
    db.refresh(store)

    return {
        "message": "Store updated successfully",
        "id": str(store.id)
    }


@router.delete("/{store_id}", summary="删除店铺")
async def delete_store(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    删除店铺
    """
    store = db.query(AmazonStore).filter(
        AmazonStore.id == store_id,
        AmazonStore.user_id == current_user["id"]
    ).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # TODO: 检查是否有关联数据，提示用户
    # 关联数据会通过 CASCADE 自动删除

    db.delete(store)
    db.commit()

    return {
        "message": "Store deleted successfully"
    }


@router.post("/{store_id}/verify", summary="验证凭证")
async def verify_credentials(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    验证店铺的 API 凭证是否有效
    """
    store = db.query(AmazonStore).filter(
        AmazonStore.id == store_id,
        AmazonStore.user_id == current_user["id"]
    ).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # 检查是否配置了凭证
    if not store.sp_api_refresh_token and not store.advertising_api_refresh_token:
        return {
            "valid": False,
            "message": "No credentials configured"
        }

    try:
        # 尝试触发一个轻量级的同步任务来验证凭证
        # 这里使用 1 天的数据来快速验证
        task = sync_inventory_task.delay(
            store_id=str(store_id),
            days=1,
            use_mock=False
        )

        return {
            "valid": True,
            "message": "Credentials verification started",
            "task_id": task.id
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Verification failed: {str(e)}"
        }


@router.get("/{store_id}/sync-history", summary="获取同步历史")
async def get_store_sync_history(
    store_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取指定店铺的同步历史记录
    """
    # 验证店铺所有权
    store = db.query(AmazonStore).filter(
        AmazonStore.id == store_id,
        AmazonStore.user_id == current_user["id"]
    ).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    query = db.query(SyncTask).filter(SyncTask.store_id == store_id)

    if status:
        query = query.filter(SyncTask.status == status)

    total = query.count()
    tasks = query.order_by(SyncTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(t.id),
                "store_id": str(t.store_id),
                "sync_type": t.sync_type,
                "status": t.status,
                "start_time": t.start_time.isoformat(),
                "end_time": t.end_time.isoformat() if t.end_time else None,
                "records_synced": t.records_synced,
                "records_failed": t.records_failed,
                "error_message": t.error_message,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ]
    }
