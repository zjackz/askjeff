from __future__ import annotations

from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import psutil

from app.api.deps import get_db
from app.services.audit_service import AuditService
from app.models.import_batch import ImportBatch, ProductRecord
from app.models.extraction_run import ExtractionRun

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


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取仪表盘汇总统计数据（用于图表）。"""
    # 1. 任务趋势 (最近7天)
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    # 导入趋势
    import_trends = db.query(
        func.date(ImportBatch.created_at).label('date'),
        func.count(ImportBatch.id).label('count')
    ).filter(ImportBatch.created_at >= seven_days_ago)\
     .group_by(func.date(ImportBatch.created_at))\
     .all()
    
    # 提取趋势
    extraction_trends = db.query(
        func.date(ExtractionRun.created_at).label('date'),
        func.count(ExtractionRun.id).label('count')
    ).filter(ExtractionRun.created_at >= seven_days_ago)\
     .group_by(func.date(ExtractionRun.created_at))\
     .all()
    
    # 填充缺失日期
    trend_data = []
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        date_str = date.isoformat()
        
        import_count = next((t.count for t in import_trends if t.date == date), 0)
        extraction_count = next((t.count for t in extraction_trends if t.date == date), 0)
        
        trend_data.append({
            "date": date_str,
            "imports": import_count,
            "extractions": extraction_count
        })
    
    # 2. 类目分布 (Top 10)
    category_dist = db.query(
        ProductRecord.category,
        func.count(ProductRecord.id).label('count')
    ).filter(ProductRecord.category != None)\
     .group_by(ProductRecord.category)\
     .order_by(desc('count'))\
     .limit(10)\
     .all()
    
    # 3. 总体统计
    total_batches = db.query(func.count(ImportBatch.id)).scalar()
    total_products = db.query(func.count(ProductRecord.id)).scalar()
    total_extractions = db.query(func.count(ExtractionRun.id)).scalar()
    
    return {
        "trends": trend_data,
        "categories": [
            {"name": c.category or "未知", "value": c.count}
            for c in category_dist
        ],
        "stats": {
            "batches": total_batches or 0,
            "products": total_products or 0,
            "extractions": total_extractions or 0
        }
    }
