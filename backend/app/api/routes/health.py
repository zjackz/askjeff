"""健康检查端点

提供系统健康状态检查
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter
from sqlalchemy import text

from app.db import SessionLocal
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    检查:
    - 数据库连接
    - 存储目录
    - 系统状态
    """
    checks = {
        "status": "healthy",
        "checks": {}
    }
    
    # 1. 数据库检查
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        checks["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["checks"]["database"] = "unhealthy"
        checks["status"] = "unhealthy"
    
    # 2. 存储目录检查
    try:
        storage_path = Path(settings.storage_dir)
        if storage_path.exists() and storage_path.is_dir():
            checks["checks"]["storage"] = "healthy"
        else:
            checks["checks"]["storage"] = "unhealthy"
            checks["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        checks["checks"]["storage"] = "unhealthy"
        checks["status"] = "unhealthy"
    
    # 3. DeepSeek API 检查 (可选,避免频繁调用外部 API)
    # 这里只检查配置是否存在
    if settings.deepseek_api_key:
        checks["checks"]["deepseek_config"] = "configured"
    else:
        checks["checks"]["deepseek_config"] = "not_configured"
    
    return checks


@router.get("/health/ready")
async def readiness_check():
    """
    就绪检查 - 用于 Kubernetes readiness probe
    
    只有当所有关键服务都正常时才返回 200
    """
    try:
        # 数据库检查
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        
        # 存储检查
        storage_path = Path(settings.storage_dir)
        if not (storage_path.exists() and storage_path.is_dir()):
            return {"status": "not_ready", "reason": "storage_unavailable"}, 503
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "reason": str(e)}, 503


@router.get("/health/live")
async def liveness_check():
    """
    存活检查 - 用于 Kubernetes liveness probe
    
    只要进程还活着就返回 200
    """
    return {"status": "alive"}
