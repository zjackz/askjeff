from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.import_batch import ImportBatch, ProductRecord


class ImportRepository:
    @staticmethod
    def create_batch(
        db: Session,
        *,
        filename: str,
        storage_path: str,
        import_strategy: str,
        created_by: str | None = None,
    ) -> ImportBatch:
        batch = ImportBatch(
            filename=filename,
            storage_path=storage_path,
            import_strategy=import_strategy,
            status="pending",
            created_by=created_by,
            started_at=datetime.now(timezone.utc),
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch

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
    ) -> ImportBatch:
        batch.status = status
        batch.total_rows = total_rows
        batch.success_rows = success_rows
        batch.failed_rows = failed_rows
        batch.failure_summary = failure_summary
        batch.finished_at = datetime.now(timezone.utc)
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
    def get_batch(db: Session, batch_id: str) -> ImportBatch | None:
        return db.get(ImportBatch, batch_id)

    @staticmethod
    def list_products(
        db: Session,
        *,
        batch_id: str | None = None,
        asin: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[ProductRecord], int]:
        stmt = select(ProductRecord)
        count_stmt = select(func.count())
        if batch_id:
            stmt = stmt.where(ProductRecord.batch_id == batch_id)
            count_stmt = count_stmt.where(ProductRecord.batch_id == batch_id)
        if asin:
            stmt = stmt.where(ProductRecord.asin == asin)
            count_stmt = count_stmt.where(ProductRecord.asin == asin)
        if status:
            stmt = stmt.where(ProductRecord.validation_status == status)
            count_stmt = count_stmt.where(ProductRecord.validation_status == status)
        stmt = stmt.order_by(ProductRecord.ingested_at.desc())
        total = db.scalar(count_stmt) or 0
        items = (
            db.execute(stmt.offset((page - 1) * page_size).limit(page_size))
            .scalars()
            .all()
        )
        return items, int(total)
