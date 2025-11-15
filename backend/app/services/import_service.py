from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.import_batch import ProductRecord
from app.services.audit_service import AuditService
from app.services.import_repository import ImportRepository


@dataclass
class ParsedResult:
    records: list[ProductRecord]
    failures: list[dict]


class ImportService:
    def __init__(self) -> None:
        self.import_dir = settings.storage_dir / "imports"
        self.import_dir.mkdir(parents=True, exist_ok=True)

    def handle_upload(
        self,
        db: Session,
        *,
        file: UploadFile,
        import_strategy: str,
        created_by: str | None = None,
    ):
        saved_path = self._save_file(file)
        batch = ImportRepository.create_batch(
            db,
            filename=file.filename,
            storage_path=str(saved_path),
            import_strategy=import_strategy,
            created_by=created_by,
        )

        parsed = self._parse_file(saved_path, batch_id=batch.id)
        if parsed.records:
            ImportRepository.create_product_records(db, parsed.records)
        failure_file = None
        if parsed.failures:
            failure_file = self._write_failures(batch.id, parsed.failures)
        status = "succeeded" if not parsed.failures else "failed"
        ImportRepository.update_batch_stats(
            db,
            batch,
            status=status,
            total_rows=len(parsed.records) + len(parsed.failures),
            success_rows=len(parsed.records),
            failed_rows=len(parsed.failures),
            failure_summary={
                "items": parsed.failures,
                "file": str(failure_file) if failure_file else None,
            }
            if parsed.failures
            else None,
        )
        AuditService.log_action(
            db,
            action="import.create",
            actor_id=created_by,
            entity_id=batch.id,
            payload={
                "filename": file.filename,
                "status": status,
                "failed_rows": len(parsed.failures),
            },
        )
        return batch

    def _save_file(self, file: UploadFile) -> Path:
        suffix = Path(file.filename or "upload").suffix or ".csv"
        target = self.import_dir / f"{uuid4()}{suffix}"
        with target.open("wb") as dest:
            dest.write(file.file.read())
        file.file.seek(0)
        return target

    def _parse_file(self, path: Path, *, batch_id: str) -> ParsedResult:
        records: list[ProductRecord] = []
        failures: list[dict] = []
        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for idx, row in enumerate(reader, start=2):
                asin = row.get("asin") or row.get("ASIN")
                title = row.get("title") or row.get("Title")
                if not asin or not title:
                    failures.append({"row": idx, "reason": "缺少 ASIN 或标题"})
                    continue
                record = ProductRecord(
                    batch_id=batch_id,
                    asin=asin,
                    title=title,
                    category=row.get("category"),
                    price=self._to_float(row.get("price")),
                    currency=row.get("currency"),
                    sales_rank=self._to_int(row.get("sales_rank")),
                    reviews=self._to_int(row.get("reviews")),
                    rating=self._to_float(row.get("rating")),
                    raw_payload=row,
                    normalized_payload=row,
                )
                records.append(record)
        return ParsedResult(records=records, failures=failures)

    def _write_failures(self, batch_id: str, failures: list[dict]) -> Path:
        target = self.import_dir / f"{batch_id}_failed.csv"
        with target.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=["row", "reason"])
            writer.writeheader()
            for item in failures:
                writer.writerow(item)
        return target

    @staticmethod
    def _to_float(value: str | None) -> float | None:
        if value in (None, ""):
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _to_int(value: str | None) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except ValueError:
            return None


import_service = ImportService()
