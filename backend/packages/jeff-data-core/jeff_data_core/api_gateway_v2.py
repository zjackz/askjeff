"""
Jeff Data Core API Gateway

统一的 API 入口，集成认证、日志、租户管理
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4
import time

# JDC 导入
from .auth import TenantAuthMiddleware, get_current_tenant, generate_api_key, regenerate_api_key as regenerate
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
    from app.models.jdc_models import JDC_Tenant

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
        api_key = generate_api_key(tenant_id)

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

        return {
            "success": True,
            "tenant_id": str(tenant.id),
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
        new_api_key = regenerate(db, tenant_id)

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
        from datetime import timedelta

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
        # 创建数据源
        data_source = JDC_DataSource(
            tenant_id=tenant_id,
            source_type=source_config.get("source_type"),
            config=source_config,
            is_active=source_config.get("is_active", True),
            sync_frequency=source_config.get("sync_frequency", "daily")
        )
        db.add(data_source)
        db.commit()

        return {
            "success": True,
            "data_source_id": str(data_source.id)
        }
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
    source_type: Optional[str] = None
):
    """列出数据源"""
    tenant_id = request.state.tenant_id

    db = SessionLocal()
    try:
        query = db.query(JDC_DataSource).filter(JDC_DataSource.tenant_id == tenant_id)

        if source_type:
            query = query.filter(JDC_DataSource.source_type == source_type)

        sources = query.all()

        return {
            "success": True,
            "data_sources": [
                {
                    "id": str(source.id),
                    "source_type": source.source_type,
                    "is_active": source.is_active,
                    "last_sync_at": source.last_sync_at.isoformat() if source.last_sync_at else None,
                    "sync_frequency": source.sync_frequency
                }
                for source in sources
            ]
        }
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

    # TODO: 实现数据同步触发逻辑
    return {
        "success": True,
        "sync_task_id": "xxx"
    }


@router.get("/data-sources/{source_id}/sync-status", tags=["Data Source Management"])
async def get_sync_status(
    request: Request,
    source_id: str
):
    """获取同步状态"""
    # TODO: 实现同步状态查询逻辑
    return {
        "status": "running",
        "progress": 45,
        "records_synced": 1500
    }


# ============================================================================
# 数据查询 API
# ============================================================================

@router.get("/products", tags=["Data Query"])
async def query_products(
    request: Request,
    filters: Dict[str, Any],
    date_range: Optional[str] = None
):
    """查询产品数据"""
    tenant_id = request.state.tenant_id

    # TODO: 实现产品查询逻辑
    return {
        "success": True,
        "products": [],
        "total": 0
    }


@router.get("/products/{product_id}", tags=["Data Query"])
async def get_product_detail(
    request: Request,
    product_id: str
):
    """获取产品详情"""
    tenant_id = request.state.tenant_id

    # TODO: 实现产品详情查询逻辑
    return {
        "success": True,
        "product": {}
    }


@router.get("/products/time-series", tags=["Data Query"])
async def get_product_time_series(
    request: Request,
    product_id: str,
    metrics: str,
    start_date: str,
    end_date: str
):
    """获取产品时间序列数据"""
    tenant_id = request.state.tenant_id

    # TODO: 实现时间序列数据查询逻辑
    return {
        "success": True,
        "time_series": []
    }


# ============================================================================
# AI 服务 API
# ============================================================================

@router.post("/ai/chat", tags=["AI Services"])
async def chat(
    request: Request,
    messages: List[Dict[str, str]],
    provider: str = "deepseek",
    model: Optional[str] = None
):
    """AI 对话"""
    tenant_id = request.state.tenant_id

    # 检查速率限制
    # from .auth import check_rate_limit
    # if not check_rate_limit(request, tenant_id, "ai"):
    #     raise JDCException(
    #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #         detail="AI API rate limit exceeded"
    #     )

    # 创建带日志的 AI 服务
    # ai_service = AIServiceWithLogging(
    #     ai_service=AIService(config),
    #     log_storage=None,  # TODO: 创建 LogStorage 实例
    #     tenant_id=tenant_id
    # )

    try:
        # result = await ai_service.chat(
        #     messages=messages,
        #     provider=provider,
        #     model=model
        # )

        return {
            "success": True,
            "content": "AI response (TODO)",
            "provider": provider,
            "model": model
        }
    except Exception as e:
        raise JDCException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat failed: {str(e)}"
        )


@router.post("/ai/extract-features", tags=["AI Services"])
async def extract_features(
    request: Request,
    products: List[Dict[str, Any]],
    provider: str = "deepseek"
):
    """AI 特征提取"""
    tenant_id = request.state.tenant_id

    # TODO: 实现 AI 特征提取逻辑
    return {
        "success": True,
        "features": {}
    }


@router.post("/ai/analyze-ads", tags=["AI Services"])
async def analyze_ads(
    request: Request,
    ads_data: Dict[str, Any],
    provider: str = "deepseek"
):
    """AI 广告诊断"""
    tenant_id = request.state.tenant_id

    # TODO: 实现 AI 广告分析逻辑
    return {
        "success": True,
        "analysis": "AI analysis result (TODO)"
    }


# ============================================================================
# 日志和监控 API
# ============================================================================

@router.get("/logs/api-calls", tags=["Logging & Monitoring"])
async def get_api_call_logs(
    request: Request,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    api_type: Optional[str] = None
):
    """查询 API 调用日志"""
    tenant_id = request.state.tenant_id

    # TODO: 实现日志查询逻辑
    return {
        "success": True,
        "logs": [],
        "total": 0
    }


@router.get("/logs/sync-tasks", tags=["Logging & Monitoring"])
async def get_sync_task_logs(
    request: Request,
    status: Optional[str] = None
):
    """查询同步任务日志"""
    tenant_id = request.state.tenant_id

    # TODO: 实现同步任务日志查询逻辑
    return {
        "success": True,
        "tasks": [],
        "total": 0
    }


@router.get("/logs/ai-calls", tags=["Logging & Monitoring"])
async def get_ai_call_logs(
    request: Request,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """查询 AI 调用日志"""
    tenant_id = request.state.tenant_id

    # TODO: 实现 AI 调用日志查询逻辑
    return {
        "success": True,
        "logs": [],
        "total": 0
    }


@router.get("/metrics/performance", tags=["Logging & Monitoring"])
async def get_performance_metrics(
    request: Request,
    metric_type: str,
    start_time: str,
    end_time: str
):
    """查询性能指标"""
    tenant_id = request.state.tenant_id

    # TODO: 实现性能指标查询逻辑
    return {
        "success": True,
        "metrics": []
    }
