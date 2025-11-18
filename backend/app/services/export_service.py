from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ExportJob, ProductRecord
from app.services.audit_service import AuditService
from app.services.log_service import LogService


@dataclass
class ExportResult:
    file_path: Path
    rows: int


class ExportService:
    def __init__(self) -> None:
        self.export_dir = settings.storage_dir / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def normalize_export_type(export_type: str) -> str:
        mapping = {
            "clean-products": "clean_products",
            "clean_products": "clean_products",
            "failed-rows": "failed_rows",
            "failed_rows": "failed_rows",
        }
        normalized = mapping.get(export_type)
        if not normalized:
            raise ValueError("不支持的导出类型")
        return normalized

    @staticmethod
    def normalize_file_format(file_format: str) -> str:
        fmt = (file_format or "csv").lower()
        if fmt not in {"csv", "xlsx"}:
            raise ValueError("不支持的导出文件格式")
        return fmt

    def create_job(
        self,
        db: Session,
        *,
        export_type: str,
        filters: dict | None,
        selected_fields: list[str],
        file_format: str,
        triggered_by: str | None = None,
    ) -> ExportJob:
        normalized_type = self.normalize_export_type(export_type)
        normalized_format = self.normalize_file_format(file_format)
        job = ExportJob(
            export_type=normalized_type,
            filters=filters,
            selected_fields=selected_fields,
            file_format=normalized_format,
            status="running",
            started_at=datetime.now(timezone.utc),
            triggered_by=triggered_by,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            result = self._generate_file(db, job)
            job.file_path = str(result.file_path)
            job.status = "succeeded"
            job.finished_at = datetime.now(timezone.utc)
            job.error_message = None
            LogService.log(
                db,
                level="info",
                category="export",
                message=f"导出完成，任务 {job.id}",
                context={
                    "export_type": job.export_type,
                    "file_format": job.file_format,
                    "rows": result.rows,
                    "file_path": job.file_path,
                },
                trace_id=job.id,
            )
        except Exception as exc:  # noqa: BLE001
            job.status = "failed"
            job.error_message = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            LogService.log(
                db,
                level="error",
                category="export",
                message=f"导出失败，任务 {job.id}",
                context={
                    "export_type": job.export_type,
                    "file_format": job.file_format,
                    "error": str(exc),
                },
                trace_id=job.id,
            )
        finally:
            db.add(job)
            db.commit()
            db.refresh(job)
            AuditService.log_action(
                db,
                action="export.create",
                actor_id=triggered_by,
                entity_id=job.id,
                payload={"status": job.status, "file_path": job.file_path},
            )
        return job

    def _generate_file(self, db: Session, job: ExportJob) -> ExportResult:
        rows = self._fetch_rows(db, job.filters)
        filename = self.export_dir / f"{job.id}.{job.file_format}"
        if job.file_format == "csv":
            with filename.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=job.selected_fields)
                writer.writeheader()
                for item in rows:
                    writer.writerow({field: item.get(field) for field in job.selected_fields})
        else:
            # 简化：xlsx 仍以 csv 生成
            with filename.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=job.selected_fields)
                writer.writeheader()
                for item in rows:
                    writer.writerow({field: item.get(field) for field in job.selected_fields})
        return ExportResult(file_path=filename, rows=len(rows))

    def _fetch_rows(self, db: Session, filters: dict | None) -> Sequence[dict]:
        stmt = select(ProductRecord)
        if filters:
            batch_id = filters.get("batch_id")
            if batch_id:
                stmt = stmt.where(ProductRecord.batch_id == batch_id)
            status = filters.get("validation_status")
            if status:
                stmt = stmt.where(ProductRecord.validation_status == status)
        records = db.execute(stmt).scalars().all()
        return [
            {
                "batch_id": item.batch_id,
                "asin": item.asin,
                "title": item.title,
                "price": item.price,
                "validation_status": item.validation_status,
            }
            for item in records
        ]

    def get_job(self, db: Session, job_id: str) -> ExportJob | None:
        return db.get(ExportJob, job_id)


export_service = ExportService()
