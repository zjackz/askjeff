from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.products import ProductListResponse
from app.services.import_repository import ImportRepository

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    batch_id: int | None = Query(None, description="导入批次ID", alias="batchId"),
    asin: str | None = Query(default=None),
    status: str | None = Query(default=None, alias="status"),
    updated_from: str | None = Query(default=None, alias="updated_from"),
    updated_to: str | None = Query(default=None, alias="updated_to"),
    min_price: float | None = Query(default=None, alias="minPrice"),
    max_price: float | None = Query(default=None, alias="maxPrice"),
    min_rating: float | None = Query(default=None, alias="minRating"),
    max_rating: float | None = Query(default=None, alias="maxRating"),
    min_reviews: int | None = Query(default=None, alias="minReviews"),
    max_reviews: int | None = Query(default=None, alias="maxReviews"),
    min_rank: int | None = Query(default=None, alias="minRank"),
    max_rank: int | None = Query(default=None, alias="maxRank"),
    category: str | None = Query(default=None),
    sort_by: str | None = Query(default=None, alias="sortBy"),
    sort_order: str | None = Query(default=None, alias="sortOrder"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=200),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    parsed_from = _parse_dt(updated_from)
    parsed_to = _parse_dt(updated_to)
    items, total = ImportRepository.list_products(
        db,
        batch_id=batch_id,
        asin=asin,
        status=status,
        updated_from=parsed_from,
        updated_to=parsed_to,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        max_rating=max_rating,
        min_reviews=min_reviews,
        max_reviews=max_reviews,
        min_rank=min_rank,
        max_rank=max_rank,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return ProductListResponse(items=items, total=total)
