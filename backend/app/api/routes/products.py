from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.products import ProductListResponse
from app.services.import_repository import ImportRepository

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    batch_id: str | None = Query(default=None, alias="batchId"),
    asin: str | None = Query(default=None),
    status: str | None = Query(default=None, alias="status"),
    updated_from: str | None = Query(default=None, alias="updated_from"),
    updated_to: str | None = Query(default=None, alias="updated_to"),
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
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return ProductListResponse(items=items, total=total)
