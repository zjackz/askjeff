from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ExportJob, ProductRecord
from app.services.audit_service import AuditService
from app.services.log_service import LogService
from app.utils.time import utc_now
from app.models.extraction_run import ExtractionRun

ALLOWED_EXPORT_FIELDS = {"asin", "title", "price", "batch_id", "validation_status", "currency"}


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
            "extraction_results": "extraction_results",
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

    @staticmethod
    def _validate_fields(selected_fields: list[str], export_type: str = "") -> list[str]:
        if export_type == "extraction_results":
            # For extraction results, we allow any fields (dynamic)
            return selected_fields
            
        fields = [f for f in selected_fields if f in ALLOWED_EXPORT_FIELDS]
        if not fields:
            raise ValueError("请选择至少一个允许导出的字段")
        return fields

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
            selected_fields=self._validate_fields(selected_fields, normalized_type),
            file_format=normalized_format,
            status="running",
            started_at=utc_now(),
            triggered_by=triggered_by,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            result = self._generate_file(db, job)
            job.file_path = str(result.file_path)
            job.status = "succeeded"
            job.finished_at = utc_now()
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
            job.finished_at = utc_now()
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
        rows = self._fetch_rows(db, job.export_type, job.filters)
        filename = self.export_dir / f"{job.id}.{job.file_format}"
        
        # Determine fields to write
        fields = job.selected_fields
        if not fields and rows:
            # If no fields selected (or dynamic), use keys from first row
            fields = list(rows[0].keys())
            
        if job.file_format == "csv":
            with filename.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields)
                writer.writeheader()
                for item in rows:
                    writer.writerow({field: item.get(field) for field in fields})
        else:
            # Real XLSX generation with styling
            self._generate_xlsx(filename, fields, rows, job)
        return ExportResult(file_path=filename, rows=len(rows))
    
    def _generate_xlsx(self, filename: Path, fields: list[str], rows: list[dict], job: ExportJob) -> None:
        """Generate XLSX file with styling for AI columns."""
        from openpyxl import Workbook
        from openpyxl.styles import PatternFill, Font
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Export Data"
        
        # Identify AI columns for extraction_results
        ai_columns = set()
        if job.export_type == "extraction_results" and rows:
            # Get run to identify target fields
            run_id = job.filters.get("run_id") if job.filters else None
            if run_id:
                from app.models.extraction_run import ExtractionRun
                from sqlalchemy.orm import Session
                run = job  # We need db session here, will get it from context
                # For now, identify AI columns by checking if they exist in ai_features
                first_row = rows[0]
                # AI columns are those that are NOT in the standard product fields
                standard_fields = {"asin", "title", "category", "price", "currency", "sales_rank", "reviews", "rating"}
                ai_columns = {field for field in fields if field not in standard_fields}
        
        # Yellow fill for AI columns
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        bold_font = Font(bold=True)
        
        # Write header row
        for col_idx, field in enumerate(fields, start=1):
            cell = ws.cell(row=1, column=col_idx, value=field)
            cell.font = bold_font
            if field in ai_columns:
                cell.fill = yellow_fill
        
        # Write data rows
        for row_idx, row_data in enumerate(rows, start=2):
            for col_idx, field in enumerate(fields, start=1):
                value = row_data.get(field)
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        # Auto-adjust column widths
        for col_idx, field in enumerate(fields, start=1):
            max_length = len(str(field))
            for row_data in rows[:100]:  # Sample first 100 rows for performance
                cell_value = str(row_data.get(field, ""))
                max_length = max(max_length, len(cell_value))
            # Set width (with some padding)
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_length + 2, 50)
        
        wb.save(filename)

    def _fetch_rows(self, db: Session, export_type: str, filters: dict | None) -> Sequence[dict]:
        if export_type == "extraction_results":
            return self._fetch_extraction_rows(db, filters)

        stmt = select(ProductRecord)
        if filters:
            batch_id = filters.get("batch_id")
            if batch_id:
                # Convert to int if it's a string
                batch_id_int = int(batch_id) if isinstance(batch_id, str) else batch_id
                stmt = stmt.where(ProductRecord.batch_id == batch_id_int)
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

    def _fetch_extraction_rows(self, db: Session, filters: dict | None) -> Sequence[dict]:
        if not filters or not filters.get("run_id"):
            raise ValueError("导出提取结果需要指定 run_id")
            
        run_id = filters.get("run_id")
        run = db.get(ExtractionRun, run_id)
        if not run:
            raise ValueError("找不到指定的提取记录")
            
        stmt = select(ProductRecord).where(ProductRecord.batch_id == run.batch_id)
        records = db.execute(stmt).scalars().all()
        
        results = []
        for record in records:
            # 1. Start with Standard Fields
            row = {
                "asin": record.asin,
                "title": record.title,
                "price": record.price,
                "currency": record.currency,
                "category": record.category,
                "sales_rank": record.sales_rank,
                "reviews": record.reviews,
                "rating": record.rating,
            }
            
            # 2. Merge Original Data (raw_payload) - optional, but good for context
            # Be careful not to overwrite standard fields with raw/unnormalized data if we want clean data
            # But user might expect original columns. Let's merge raw_payload but keep standard fields if they exist?
            # Actually, let's just add raw_payload keys that are NOT in standard fields
            if record.raw_payload:
                for k, v in record.raw_payload.items():
                    if k not in row:
                        row[k] = v
            
            # 3. Merge AI Features
            if record.ai_features:
                row.update(record.ai_features)
                
            results.append(row)
            
        return results

    def list_jobs(self, db: Session, limit: int = 20, offset: int = 0) -> list[ExportJob]:
        """获取导出任务列表,按开始时间倒序"""
        stmt = select(ExportJob).order_by(ExportJob.started_at.desc()).limit(limit).offset(offset)
        return list(db.execute(stmt).scalars().all())

    def get_job(self, db: Session, job_id: str) -> ExportJob | None:
        return db.get(ExportJob, job_id)


export_service = ExportService()
