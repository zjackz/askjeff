from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.import_batch import ImportBatch, ProductRecord


class ImportRepository:
    @staticmethod
    def create_batch(
        db: Session,
        *,
        filename: str,
        storage_path: str,
        import_strategy: str,
        sheet_name: str | None = None,
        created_by: str | None = None,
        file_hash: str | None = None,
    ) -> ImportBatch:
        batch = ImportBatch(
            filename=filename,
            storage_path=storage_path,
            import_strategy=import_strategy,
            status="pending",
            sheet_name=sheet_name,
            created_by=created_by,
            started_at=datetime.now(timezone.utc),
            file_hash=file_hash,
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch

    @staticmethod
    def find_batch_by_hash(db: Session, file_hash: str) -> ImportBatch | None:
        stmt = select(ImportBatch).where(
            ImportBatch.file_hash == file_hash,
            ImportBatch.status == "succeeded"
        ).limit(1)
        return db.scalar(stmt)

    @staticmethod
    def update_batch_stats(
        db: Session,
        batch: ImportBatch,
        *,
        status: str,
        total_rows: int,
        success_rows: int,
        failed_rows: int,
        failure_summary: dict | None = None,
        columns_seen: list[str] | None = None,
    ) -> ImportBatch:
        batch.status = status
        batch.total_rows = total_rows
        batch.success_rows = success_rows
        batch.failed_rows = failed_rows
        batch.failure_summary = failure_summary
        batch.columns_seen = columns_seen
        batch.finished_at = datetime.now(timezone.utc)
        db.add(batch)
        db.commit()
        db.refresh(batch)
        db.refresh(batch)
        return batch

    @staticmethod
    def update_batch_progress(
        db: Session,
        batch: ImportBatch,
        *,
        status: str,
        total_rows: int,
    ) -> ImportBatch:
        batch.status = status
        batch.total_rows = total_rows
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch

    @staticmethod
    def create_product_records(db: Session, records: list[ProductRecord]) -> None:
        db.add_all(records)
        db.commit()

    @staticmethod
    def list_batches(db: Session, *, status: str | None = None) -> Sequence[ImportBatch]:
        return ImportRepository.list_batches_with_filters(db, status=status)[0]

    @staticmethod
    def list_batches_with_filters(
        db: Session,
        *,
        status: str | None = None,
        asin: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[ImportBatch], int]:
        stmt = select(ImportBatch)
        count_stmt = select(func.count(func.distinct(ImportBatch.id)))
        if status:
            stmt = stmt.where(ImportBatch.status == status)
            count_stmt = count_stmt.where(ImportBatch.status == status)
        if asin:
            stmt = (
                stmt.join(ProductRecord, ProductRecord.batch_id == ImportBatch.id)
                .where(ProductRecord.asin == asin)
                .distinct()
            )
            count_stmt = (
                count_stmt.join(ProductRecord, ProductRecord.batch_id == ImportBatch.id)
                .where(ProductRecord.asin == asin)
            )
        stmt = stmt.order_by(ImportBatch.started_at.desc().nullslast())
        total = db.scalar(count_stmt) or 0
        items = (
            db.execute(stmt.offset((page - 1) * page_size).limit(page_size))
            .scalars()
            .all()
        )
        return items, int(total)

    @staticmethod
    def get_batch(db: Session, batch_id: int) -> ImportBatch | None:
        return db.get(ImportBatch, batch_id)

    @staticmethod
    def list_products(
        db: Session,
        *,
        batch_id: int | None = None,
        asin: str | None = None,
        status: str | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        min_reviews: int | None = None,
        max_reviews: int | None = None,
        min_rank: int | None = None,
        max_rank: int | None = None,
        category: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[ProductRecord], int]:
        stmt = select(ProductRecord).options(joinedload(ProductRecord.batch))
        count_stmt = select(func.count())
        if batch_id:
            stmt = stmt.where(ProductRecord.batch_id == batch_id)
            count_stmt = count_stmt.where(ProductRecord.batch_id == batch_id)
        if asin:
            like_pattern = f"%{asin}%"
            stmt = stmt.where(
                ProductRecord.asin.ilike(like_pattern) | ProductRecord.title.ilike(like_pattern)
            )
            count_stmt = count_stmt.where(
                ProductRecord.asin.ilike(like_pattern) | ProductRecord.title.ilike(like_pattern)
            )
        if status:
            normalized = status.lower()
            status_map = {
                "success": "valid",
                "succeeded": "valid",
                "failed": "error",
                "error": "error",
                "pending": "warning",
                "warning": "warning",
            }
            resolved = status_map.get(normalized, normalized)
            stmt = stmt.where(ProductRecord.validation_status == resolved)
            count_stmt = count_stmt.where(ProductRecord.validation_status == resolved)
        if updated_from:
            stmt = stmt.where(ProductRecord.ingested_at >= updated_from)
            count_stmt = count_stmt.where(ProductRecord.ingested_at >= updated_from)
        if updated_to:
            stmt = stmt.where(ProductRecord.ingested_at <= updated_to)
            count_stmt = count_stmt.where(ProductRecord.ingested_at <= updated_to)
        
        # 范围查询
        if min_price is not None:
            stmt = stmt.where(ProductRecord.price >= min_price)
            count_stmt = count_stmt.where(ProductRecord.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(ProductRecord.price <= max_price)
            count_stmt = count_stmt.where(ProductRecord.price <= max_price)
            
        if min_rating is not None:
            stmt = stmt.where(ProductRecord.rating >= min_rating)
            count_stmt = count_stmt.where(ProductRecord.rating >= min_rating)
        if max_rating is not None:
            stmt = stmt.where(ProductRecord.rating <= max_rating)
            count_stmt = count_stmt.where(ProductRecord.rating <= max_rating)
            
        if min_reviews is not None:
            stmt = stmt.where(ProductRecord.reviews >= min_reviews)
            count_stmt = count_stmt.where(ProductRecord.reviews >= min_reviews)
        if max_reviews is not None:
            stmt = stmt.where(ProductRecord.reviews <= max_reviews)
            count_stmt = count_stmt.where(ProductRecord.reviews <= max_reviews)
            
        if min_rank is not None:
            stmt = stmt.where(ProductRecord.sales_rank >= min_rank)
            count_stmt = count_stmt.where(ProductRecord.sales_rank >= min_rank)
        if max_rank is not None:
            stmt = stmt.where(ProductRecord.sales_rank <= max_rank)
            count_stmt = count_stmt.where(ProductRecord.sales_rank <= max_rank)
            
        if category:
            stmt = stmt.where(ProductRecord.category.ilike(f"%{category}%"))
            count_stmt = count_stmt.where(ProductRecord.category.ilike(f"%{category}%"))
        order_field = ProductRecord.ingested_at
        sort_map = {
            "ingested_at": ProductRecord.ingested_at,
            "status": ProductRecord.validation_status,
            "validation_status": ProductRecord.validation_status,
            "asin": ProductRecord.asin,
            "batch_id": ProductRecord.batch_id,
            "price": ProductRecord.price,
            "rating": ProductRecord.rating,
            "sales_rank": ProductRecord.sales_rank,
        }
        if sort_by:
            resolved_field = sort_map.get(sort_by)
            if resolved_field is not None:
                order_field = resolved_field
        if sort_order and sort_order.lower() == "asc":
            stmt = stmt.order_by(order_field.asc().nullslast())
        else:
            stmt = stmt.order_by(order_field.desc().nullslast())
        total = db.scalar(count_stmt) or 0
        items = (
            db.execute(stmt.offset((page - 1) * page_size).limit(page_size))
            .scalars()
            .all()
        )
        return items, int(total)
