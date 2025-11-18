from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.logs import (
    LogAnalyzeRequest,
    LogAnalyzeResult,
    LogIngestRequest,
    LogListResponse,
    SystemLogOut,
    LOG_LEVELS,
    LOG_CATEGORIES,
)
from app.services.log_analyzer import LogAnalyzer
from app.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/ingest", response_model=SystemLogOut, status_code=201)
async def ingest_log(payload: LogIngestRequest, db: Session = Depends(get_db)):
    level = payload.level.lower()
    category = payload.category
    if level not in LOG_LEVELS:
        raise HTTPException(status_code=400, detail="level 参数不合法")
    if category not in LOG_CATEGORIES:
        raise HTTPException(status_code=400, detail="category 参数不合法")
    entry = LogService.log(
        db,
        level=level,
        category=category,
        message=payload.message,
        context=payload.context,
        trace_id=payload.trace_id,
        status="new",
    )
    return entry


@router.get("", response_model=LogListResponse)
async def list_logs(
    level: str | None = Query(default=None),
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    startTime: datetime | None = Query(default=None),
    endTime: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    if level and level.lower() not in LOG_LEVELS:
        raise HTTPException(status_code=400, detail="level 参数不合法")
    if category and category not in LOG_CATEGORIES:
        raise HTTPException(status_code=400, detail="category 参数不合法")
    items, total = LogService.list_logs(
        db,
        level=level.lower() if level else None,
        category=category,
        keyword=keyword,
        start_time=startTime,
        end_time=endTime,
        page=page,
        page_size=pageSize,
    )
    return {"items": items, "total": total}


@router.get("/{log_id}", response_model=SystemLogOut)
async def get_log_detail(log_id: str, db: Session = Depends(get_db)):
    log = LogService.get_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log


@router.post("/analyze", response_model=LogAnalyzeResult)
async def analyze_logs(payload: LogAnalyzeRequest, db: Session = Depends(get_db)):
    if payload.level and payload.level.lower() not in LOG_LEVELS:
        raise HTTPException(status_code=400, detail="level 参数不合法")
    if payload.category and payload.category not in LOG_CATEGORIES:
        raise HTTPException(status_code=400, detail="category 参数不合法")
    if payload.log_ids:
        logs = LogService.fetch_by_ids(db, payload.log_ids[: payload.limit])
    else:
        logs, _ = LogService.list_logs(
            db,
            level=payload.level.lower() if payload.level else None,
            category=payload.category,
            keyword=payload.keyword,
            page=1,
            page_size=payload.limit,
        )
    result = LogAnalyzer.analyze(logs)
    return {
        "summary": result.summary,
        "probableCauses": result.probable_causes,
        "suggestions": result.suggestions,
        "usedAi": result.used_ai,
    }
