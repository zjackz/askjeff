# Jeff Data Core API Gateway

统一的 API 入口，集成认证、日志、租户管理
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

from .auth import TenantAuthMiddleware
from .config import JDCConfig
from .metrics import StructuredLogger
from app.models.jdc_models import JDC_Tenant, JDC_DataSource, JDC_Product, JDC_SyncTask
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
        existing = db.query(JDC_Tenant).filter(JDC_Tenant.name == tenant_data.get("name")).first()
        if existing:
            raise JDCException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant name already exists"
            )

        tenant_id = str(uuid4())
        api_key = f"jdc_{tenant_id.replace('-', '')}_{uuid4().hex[:16]}"

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
async def regenerate_api_key(
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

        new_api_key = f"jdc_{tenant_id.replace('-', '')}_{uuid4().hex[:16]}"
        tenant.api_key = new_api_key
        tenant.updated_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "tenant_id": tenant_id,
            "api_key": new_api_key
        }
    except JDCException:
        raise
    except Exception as e:
        db.rollback()
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

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        api_calls_today = db.query(JDC_ApiCallLog).filter(
            JDC_ApiCallLog.created_at >= today_start
        ).count()

        return {
            "success": True,
            "tenant_id": tenant_id,
            "name": tenant.name,
            "status": tenant.status,
            "stats": {
                "api_calls_today": api_calls_today
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
    return {
        "success": True,
        "content": "AI chat response (TODO)",
        "provider": provider,
        "model": model
    }


@router.post("/ai/extract-features", tags=["AI Services"])
async def extract_features(
    request: Request,
    products: List[Dict[str, Any]],
    provider: str = "deepseek"
):
    """AI 特征提取"""
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
    return {
        "success": True,
        "metrics": []
    }
