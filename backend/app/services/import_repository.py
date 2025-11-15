from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
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
            started_at=datetime.utcnow(),
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
        batch.finished_at = datetime.utcnow()
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
        stmt = select(ImportBatch)
        if status:
            stmt = stmt.where(ImportBatch.status == status)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_batch(db: Session, batch_id: str) -> ImportBatch | None:
        return db.get(ImportBatch, batch_id)
