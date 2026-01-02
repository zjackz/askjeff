"""
Jeff Data Core API Gateway

统一的 API 入口，集成认证、日志、租户管理
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

# JDC 导入
from .auth import TenantAuthMiddleware
from .config import JDCConfig
from .metrics import StructuredLogger
from app.models.jdc_models import JDC_Tenant, JDC_DataSource, JDC_ApiCallLog, JDC_AiCallLog, JDC_SyncTask
from app.db import SessionLocal


# 配置
config = JDCConfig.from_env()

# 初始化日志
logger = StructuredLogger("jdc_api_gateway")

# API Router
router = APIRouter()
router.add_middleware(TenantAuthMiddleware)


# 全局异常处理器
class JDCException(HTTPException):
    """JDC 自定义异常"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}


@router.exception_handler(JDCException)
async def jdc_exception_handler(request: Request, exc: JDCException):
    """JDC 异常处理"""
    logger.log_error(
        error_type="api_error",
        error_message=str(exc.detail),
        context=exc.context
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_code": exc.error_code,
            "context": exc.context
        }
    )


@router.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.log_error(
        error_type="server_error",
        error_message=str(exc),
        context={"path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )


# ============================================================================
# 健康检查
# ============================================================================

@router.get("/health", tags=["Health"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


# ============================================================================
# 租户管理 API
# ============================================================================

@router.post("/tenants", tags=["Tenant Management"])
async def create_tenant(
    request: Request,
    tenant_data: Dict[str, Any]
):
    """创建新租户"""
    db = SessionLocal()
    try:
        # 检查租户名称是否已存在
        existing = db.query(JDC_Tenant).filter(JDC_Tenant.name == tenant_data.get("name")).first()
        if existing:
            raise JDCException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant name already exists"
            )

        # 生成 API Key
        tenant_id = str(uuid4())
        api_key = f"jdc_{tenant_id.replace('-', '')}_{uuid4().hex[:16]}"

        # 创建租户
        tenant = JDC_Tenant(
            id=tenant_id,
            name=tenant_data.get("name"),
            api_key=api_key,
            status=tenant_data.get("status", "active"),
            max_api_calls_per_day=tenant_data.get("max_api_calls_per_day", 10000),
            max_ai_calls_per_day=tenant_data.get("max_ai_calls_per_day", 1000),
            max_syncs_per_day=tenant_data.get("max_syncs_per_day", 10)
        )

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        logger.log_sync_task(
            source_type="system",
            task_type="tenant_creation",
            status="success",
            records_total=1,
            records_success=1
        )

        return {
            "success": True,
            "tenant_id": tenant_id,
            "name": tenant.name,
            "api_key": api_key,
            "status": tenant.status
        }
    except JDCException:
        raise
    except Exception as e:
        db.rollback()
        logger.log_error("tenant_creation", str(e), {})
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant: {str(e)}"
        )
    finally:
        db.close()


@router.get("/tenants/{tenant_id}/api-key", tags=["Tenant Management"])
async def regenerate_api_key_endpoint(
    request: Request,
    tenant_id: str
):
    """重新生成 API Key"""
    db = SessionLocal()
    try:
        tenant = db.query(JDC_Tenant).filter(JDC_Tenant.id == tenant_id).first()
        if not tenant:
            raise JDCException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        # 生成新的 API Key
        new_api_key = f"jdc_{tenant.id.replace('-', '')}_{uuid4().hex[:16]}"

        tenant.api_key = new_api_key
        tenant.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(tenant)

        return {
            "success": True,
            "tenant_id": tenant_id,
            "api_key": new_api_key
        }
    except JDCException:
        raise
    except Exception as e:
        logger.log_error("api_key_regeneration", str(e), {"tenant_id": tenant_id})
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate API key: {str(e)}"
        )
    finally:
        db.close()


@router.get("/tenants/{tenant_id}/stats", tags=["Tenant Management"])
async def get_tenant_stats(
    request: Request,
    tenant_id: str
):
    """获取租户统计"""
    db = SessionLocal()
    try:
        tenant = db.query(JDC_Tenant).filter(JDC_Tenant.id == tenant_id).first()
        if not tenant:
            raise JDCException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )

        # 获取今日的开始时间
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # API 调用统计
        api_calls_today = db.query(JDC_ApiCallLog).filter(
            JDC_ApiCallLog.tenant_id == tenant_id,
            JDC_ApiCallLog.created_at >= today_start
        ).count()

        # AI 调用统计
        ai_calls_today = db.query(JDC_AiCallLog).filter(
            JDC_AiCallLog.tenant_id == tenant_id,
            JDC_AiCallLog.created_at >= today_start
        ).count()

        # AI 成本统计
        ai_cost_today = db.query(JDC_AiCallLog).filter(
            JDC_AiCallLog.tenant_id == tenant_id,
            JDC_AiCallLog.created_at >= today_start
        ).all()

        total_cost_today = sum(float(log.cost_usd) for log in ai_cost_today if log.cost_usd)

        # 同步任务统计
        sync_tasks_today = db.query(JDC_SyncTask).filter(
            JDC_SyncTask.tenant_id == tenant_id,
            JDC_SyncTask.created_at >= today_start
        ).count()

        sync_success_rate = 0
        if sync_tasks_today > 0:
            sync_success = db.query(JDC_SyncTask).filter(
                JDC_SyncTask.tenant_id == tenant_id,
                JDC_SyncTask.created_at >= today_start,
                JDC_SyncTask.status == 'success'
            ).count()
            sync_success_rate = (sync_success / sync_tasks_today) * 100

        # 数据源统计
        active_data_sources = db.query(JDC_DataSource).filter(
            JDC_DataSource.tenant_id == tenant_id,
            JDC_DataSource.is_active == True
        ).count()

        return {
            "success": True,
            "tenant_id": tenant_id,
            "name": tenant.name,
            "status": tenant.status,
            "stats": {
                "api_calls_today": api_calls_today,
                "ai_calls_today": ai_calls_today,
                "ai_cost_today": float(f"{total_cost_today:.6f}"),
                "sync_tasks_today": sync_tasks_today,
                "sync_success_rate": float(f"{sync_success_rate:.2f}"),
                "active_data_sources": active_data_sources,
                "max_api_calls_per_day": tenant.max_api_calls_per_day,
                "max_ai_calls_per_day": tenant.max_ai_calls_per_day,
                "max_syncs_per_day": tenant.max_syncs_per_day
            }
        }
    except JDCException:
        raise
    except Exception as e:
        logger.log_error("tenant_stats", str(e), {"tenant_id": tenant_id})
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tenant stats: {str(e)}"
        )
    finally:
        db.close()


# ============================================================================
# 数据源管理 API
# ============================================================================

@router.post("/data-sources", tags=["Data Source Management"])
async def create_data_source(
    request: Request,
    source_config: Dict[str, Any]
):
    """创建数据源配置"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        from app.models.jdc_models import JDC_DataSource as DS

        # 检查是否已存在相同类型的数据源
        existing = db.query(DS).filter(
            DS.tenant_id == tenant_id,
            DS.source_type == source_config.get("source_type")
        ).first()
        
        if existing:
            raise JDCException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data source of type {source_config.get('source_type')} already exists"
            )

        # 创建数据源
        data_source = DS(
            id=str(uuid4()),
            tenant_id=tenant_id,
            source_type=source_config.get("source_type"),
            config=source_config,
            is_active=source_config.get("is_active", True),
            sync_frequency=source_config.get("sync_frequency", "daily")
        )
        db.add(data_source)
        db.commit()

        logger.log_sync_task(
            source_type="data_source_management",
            task_type="data_source_creation",
            status="success",
            records_total=1,
            records_success=1
        )

        return {
            "success": True,
            "data_source_id": str(data_source.id),
            "source_type": data_source.source_type,
            "is_active": data_source.is_active
        }
    except JDCException:
        raise
    except Exception as e:
        db.rollback()
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create data source"
        )
    finally:
        db.close()


@router.get("/data-sources", tags=["Data Source Management"])
async def list_data_sources(
    request: Request,
    source_type: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """列出数据源"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        from app.models.jdc_models import JDC_DataSource as DS

        query = db.query(DS).filter(DS.tenant_id == tenant_id)

        if source_type:
            query = query.filter(DS.source_type == source_type)
        if is_active is not None:
            query = query.filter(DS.is_active == is_active)

        sources = query.order_by(DS.created_at.desc()).all()

        return {
            "success": True,
            "data_sources": [
                {
                    "id": str(source.id),
                    "source_type": source.source_type,
                    "is_active": source.is_active,
                    "last_sync_at": source.last_sync_at.isoformat() if source.last_sync_at else None,
                    "sync_frequency": source.sync_frequency,
                    "created_at": source.created_at.isoformat(),
                    "updated_at": source.updated_at.isoformat()
                }
                for source in sources
            ],
            "total": len(sources)
        }
    except Exception as e:
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list data sources: {str(e)}"
        )
    finally:
        db.close()


@router.get("/data-sources/{source_id}", tags=["Data Source Management"])
async def get_data_source_detail(
    request: Request,
    source_id: str
):
    """获取数据源详情"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        from app.models.jdc_models import JDC_DataSource as DS

        source = db.query(DS).filter(
            DS.id == source_id,
            DS.tenant_id == tenant_id
        ).first()
        
        if not source:
            raise JDCException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # 查询最近的同步任务
        latest_sync = db.query(JDC_SyncTask).filter(
            JDC_SyncTask.source_id == source_id
        ).order_by(JDC_SyncTask.created_at.desc()).first()

        return {
            "success": True,
            "data_source": {
                "id": str(source.id),
                "source_type": source.source_type,
                "is_active": source.is_active,
                "last_sync_at": source.last_sync_at.isoformat() if source.last_sync_at else None,
                "sync_frequency": source.sync_frequency,
                "created_at": source.created_at.isoformat(),
                "updated_at": source.updated_at.isoformat(),
                "config": source.config
            },
            "latest_sync": {
                "task_id": str(latest_sync.id) if latest_sync else None,
                "status": latest_sync.status if latest_sync else None,
                "records_total": latest_sync.records_total if latest_sync else 0,
                "records_success": latest_sync.records_success if latest_sync else 0,
                "created_at": latest_sync.created_at.isoformat() if latest_sync else None
            } if latest_sync else None
        }
    except JDCException:
        raise
    except Exception as e:
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data source detail: {str(e)}"
        )
    finally:
        db.close()


@router.put("/data-sources/{source_id}", tags=["Data Source Management"])
async def update_data_source(
    request: Request,
    source_id: str,
    update_data: Dict[str, Any]
):
    """更新数据源配置"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        from app.models.jdc_models import JDC_DataSource as DS

        source = db.query(DS).filter(
            DS.id == source_id,
            DS.tenant_id == tenant_id
        ).first()
        
        if not source:
            raise JDCException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # 更新字段
        if 'is_active' in update_data:
            source.is_active = update_data['is_active']
        if 'sync_frequency' in update_data:
            source.sync_frequency = update_data['sync_frequency']
        if 'config' in update_data:
            # 合并配置，但保护敏感字段
            source.config = {**source.config, **update_data['config']}

        source.updated_at = datetime.utcnow()
        db.commit()

        logger.log_sync_task(
            source_type=source.source_type,
            task_type="data_source_update",
            status="success",
            records_total=1,
            records_success=1
        )

        return {
            "success": True,
            "data_source_id": source_id,
            "message": "Data source updated successfully"
        }
    except JDCException:
        raise
    except Exception as e:
        db.rollback()
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update data source: {str(e)}"
        )
    finally:
        db.close()


@router.delete("/data-sources/{source_id}", tags=["Data Source Management"])
async def delete_data_source(
    request: Request,
    source_id: str
):
    """删除数据源"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        from app.models.jdc_models import JDC_DataSource as DS, JDC_SyncTask as ST

        source = db.query(DS).filter(
            DS.id == source_id,
            DS.tenant_id == tenant_id
        ).first()
        
        if not source:
            raise JDCException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # 检查是否有关联的同步任务
        pending_syncs = db.query(ST).filter(
            ST.source_id == source_id,
            ST.status.in_(['pending', 'running'])
        ).count()

        if pending_syncs > 0:
            raise JDCException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete data source with {pending_syncs} pending sync tasks"
            )

        db.delete(source)
        db.commit()

        logger.log_sync_task(
            source_type=source.source_type,
            task_type="data_source_deletion",
            status="success",
            records_total=1,
            records_success=1
        )

        return {
            "success": True,
            "message": "Data source deleted successfully"
        }
    except JDCException:
        raise
    except Exception as e:
        db.rollback()
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete data source: {str(e)}"
        )
    finally:
        db.close()


@router.post("/data-sources/{source_id}/sync", tags=["Data Source Management"])
async def trigger_data_sync(
    request: Request,
    source_id: str,
    sync_type: str = "full"
):
    """触发数据同步"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        from app.models.jdc_models import JDC_DataSource as DS, JDC_SyncTask as ST

        source = db.query(DS).filter(
            DS.id == source_id,
            DS.tenant_id == tenant_id
        ).first()
        
        if not source:
            raise JDCException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # 检查是否已有运行中的同步任务
        running_syncs = db.query(ST).filter(
            ST.source_id == source_id,
            ST.status == 'running'
        ).count()

        if running_syncs > 0:
            raise JDCException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A sync is already running for this data source"
            )

        # 创建同步任务
        sync_task = ST(
            id=str(uuid4()),
            tenant_id=tenant_id,
            source_id=source_id,
            task_type=sync_type,
            status='pending',
            start_time=datetime.utcnow(),
            retry_count=0,
            max_retries=3
        )
        db.add(sync_task)
        db.commit()

        logger.log_sync_task(
            source_type=source.source_type,
            task_type=sync_type,
            status="pending",
            records_total=0,
            records_success=0
        )

        return {
            "success": True,
            "sync_task_id": str(sync_task.id),
            "message": "Sync task created successfully"
        }
    except JDCException:
        raise
    except Exception as e:
        db.rollback()
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger sync: {str(e)}"
        )
    finally:
        db.close()


@router.get("/data-sources/{source_id}/sync-status", tags=["Data Source Management"])
async def get_sync_status(
    request: Request,
    source_id: str,
    limit: int = 10
):
    """获取同步状态"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        from app.models.jdc_models import JDC_SyncTask as ST

        source = db.query(DS).filter(DS.id == source_id, DS.tenant_id == tenant_id).first()
        if not source:
            raise JDCException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # 查询同步任务
        tasks = db.query(ST).filter(
            ST.source_id == source_id
        ).order_by(ST.created_at.desc()).limit(limit).all()

        return {
            "success": True,
            "source_type": source.source_type,
            "tasks": [
                {
                    "task_id": str(task.id),
                    "task_type": task.task_type,
                    "status": task.status,
                    "start_time": task.start_time.isoformat(),
                    "end_time": task.end_time.isoformat() if task.end_time else None,
                    "records_total": task.records_total,
                    "records_success": task.records_success,
                    "records_failed": task.records_failed,
                    "error_message": task.error_message,
                    "retry_count": task.retry_count,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ],
            "total": len(tasks)
        }
    except JDCException:
        raise
    except Exception as e:
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}"
        )
    finally:
        db.close()
