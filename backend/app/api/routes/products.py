from __future__ import annotations

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
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=200),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    items, total = ImportRepository.list_products(
        db,
        batch_id=batch_id,
        asin=asin,
        status=status,
        page=page,
        page_size=page_size,
    )
    return ProductListResponse(items=items, total=total)
