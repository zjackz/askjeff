from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models import ImportBatch
from app.services.chat_service import ToolRegistry
from app.services.import_repository import ImportRepository
from app.services.log_service import LogService


@ToolRegistry.register(
    name="query_products",
    description="查询产品列表，支持关键词搜索、排序和分页",
    parameters={
        "keyword": "搜索关键词 (ASIN 或标题)",
        "sort_by": "排序字段 (price, sales_rank, reviews, rating)",
        "sort_order": "排序方向 (asc, desc)",
        "limit": "返回数量 (默认 5, 最大 20)",
    },
)
def query_products(
    db: Session,
    keyword: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "desc",
    limit: int = 5,
) -> list[dict[str, Any]]:
    limit = min(limit, 20)
    items, _ = ImportRepository.list_products(
        db,
        asin=keyword if keyword and keyword.startswith("B0") else None,  # 简单判断 ASIN
        # title=keyword, # list_products 目前不支持 title 模糊搜索，可能需要修改 Repository 或仅支持 ASIN
        sort_by=sort_by,
        sort_order=sort_order,
        page=1,
        page_size=limit,
    )
    
    # 转换为精简字典
    results = []
    for item in items:
        results.append({
            "asin": item.asin,
            "title": item.title,
            "price": str(item.price) if item.price else None,
            "sales_rank": item.sales_rank,
            "rating": str(item.rating) if item.rating else None,
            "reviews": item.reviews,
        })
    return results


@ToolRegistry.register(
    name="get_batch_status",
    description="查询指定批次的状态和详情",
    parameters={
        "batch_id": "批次 ID (UUID)",
    },
)
def get_batch_status(db: Session, batch_id: str) -> dict[str, Any] | str:
    batch = db.get(ImportBatch, batch_id)
    if not batch:
        return f"未找到批次: {batch_id}"
    
    return {
        "batch_id": batch.id,
        "status": batch.status,
        "filename": batch.filename,
        "sheet_name": batch.sheet_name,
        "created_by": batch.created_by or "系统",
        "created_at": batch.created_at.isoformat() if batch.created_at else None,
        "started_at": batch.started_at.isoformat() if batch.started_at else None,
        "finished_at": batch.finished_at.isoformat() if batch.finished_at else None,
        "total_rows": batch.total_rows,
        "success_rows": batch.success_rows,
        "failed_rows": batch.failed_rows,
        "failure_summary": batch.failure_summary,
    }


@ToolRegistry.register(
    name="get_recent_batches",
    description="查询最近的导入批次列表",
    parameters={
        "limit": "返回数量 (默认 5)",
        "status": "按状态筛选 (可选: succeeded, failed, pending)",
    },
)
def get_recent_batches(
    db: Session, 
    limit: int = 5, 
    status: str | None = None
) -> list[dict[str, Any]]:
    limit = min(limit, 20)
    items, _ = ImportRepository.list_batches_with_filters(
        db,
        status=status,
        page=1,
        page_size=limit,
    )
    
    results = []
    for batch in items:
        results.append({
            "batch_id": batch.id,
            "filename": batch.filename,
            "status": batch.status,
            "created_by": batch.created_by or "系统",
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "summary": f"总{batch.total_rows}行 (成功{batch.success_rows}/失败{batch.failed_rows})",
        })
    return results


@ToolRegistry.register(
    name="analyze_logs",
    description="查询最近的系统日志",
    parameters={
        "level": "日志级别 (info, warning, error)",
        "limit": "返回数量 (默认 10)",
    },
)
def analyze_logs(
    db: Session,
    level: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    limit = min(limit, 50)
    items, _ = LogService.list_logs(
        db,
        level=level,
        page=1,
        page_size=limit,
    )
    
    results = []
    for log in items:
        results.append({
            "time": log.created_at.isoformat(),
            "level": log.level,
            "category": log.category,
            "message": log.message,
        })
    return results


@ToolRegistry.register(
    name="search_market_gaps",
    description="寻找蓝海市场机会（高需求、低竞争、改进空间）",
    parameters={
        "max_reviews": "最大评论数 (衡量竞争度，如 < 100)",
        "min_sales_rank": "最小排名 (衡量需求)",
        "max_sales_rank": "最大排名 (衡量需求，如 < 5000)",
        "max_rating": "最大评分 (衡量改进空间，如 < 3.8)",
        "min_price": "最低价格",
        "max_price": "最高价格",
        "category": "类目筛选",
        "limit": "返回数量 (默认 5)",
    },
)
def search_market_gaps(
    db: Session,
    max_reviews: int | None = None,
    min_sales_rank: int | None = None,
    max_sales_rank: int | None = None,
    max_rating: float | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    category: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    limit = min(limit, 20)
    
    # 默认按销量排名排序（需求优先）
    sort_by = "sales_rank"
    sort_order = "asc"
    
    items, _ = ImportRepository.list_products(
        db,
        max_reviews=max_reviews,
        min_rank=min_sales_rank,
        max_rank=max_sales_rank,
        max_rating=max_rating,
        min_price=min_price,
        max_price=max_price,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        page=1,
        page_size=limit,
    )
    
    results = []
    for item in items:
        results.append({
            "asin": item.asin,
            "title": item.title,
            "price": str(item.price) if item.price else None,
            "sales_rank": item.sales_rank,
            "rating": str(item.rating) if item.rating else None,
            "reviews": item.reviews,
            "category": item.category,
        })
    return results
