from __future__ import annotations

from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import psutil

from app.api.deps import get_db
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/activities")
async def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """获取最近的系统活动记录。"""
    logs = AuditService.get_recent_logs(db, limit=limit)
    return [
        {
            "id": log.id,
            "action": log.action,
            "actor_id": log.actor_id,
            "entity_id": log.entity_id,
            "payload": log.payload,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/system-stats")
async def get_system_stats() -> dict[str, Any]:
    """获取系统运行状态指标。"""
    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # 内存使用情况
    memory = psutil.virtual_memory()
    
    # 磁盘使用情况
    disk = psutil.disk_usage('/')
    
    # 系统启动时间
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = (datetime.now() - boot_time).total_seconds()
    
    return {
        "cpu": {
            "percent": round(cpu_percent, 1),
            "count": cpu_count,
        },
        "memory": {
            "total": memory.total,
            "used": memory.used,
            "percent": round(memory.percent, 1),
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "percent": round(disk.percent, 1),
        },
        "uptime": {
            "seconds": int(uptime_seconds),
            "boot_time": boot_time.isoformat(),
        }
    }
