import io
import json
import logging
import uuid
from typing import List

try:
    import pandas as pd
except ImportError:
    pd = None
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.extraction import ExtractionItem, ExtractionTask
from app.services.deepseek_client import DeepseekClient

logger = logging.getLogger(__name__)


class ExtractionService:
    def __init__(self, db: Session, client: DeepseekClient):
        self.db = db
        self.client = client

    async def create_task(self, file: UploadFile, target_fields: List[str] | None = None) -> ExtractionTask:
        if pd is None:
            raise ImportError("Pandas is not installed.")
        content = await file.read()
        filename = file.filename or "unknown.xlsx"
        target_fields = target_fields or []

        # Determine file type and read
        try:
            if filename.endswith(".csv"):
                # Try common encodings
                try:
                    df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(content), encoding="gbk")
            else:
                df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Failed to parse file: {e}")

        # Create Task
        task = ExtractionTask(
            filename=filename,
            target_fields=target_fields,
            status="PENDING",
        )
        self.db.add(task)
        self.db.flush()  # Get ID

        # Create Items
        items = []
        for _, row in df.iterrows():
            # Convert row to dict, handle NaN
            row_data = row.where(pd.notnull(row), None).to_dict()
            item = ExtractionItem(
                task_id=task.id,
                original_data=row_data,
                status="PENDING",
            )
            items.append(item)

        self.db.add_all(items)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_fields(self, task_id: uuid.UUID, target_fields: List[str]) -> ExtractionTask:
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        task.target_fields = target_fields
        self.db.commit()
        self.db.refresh(task)
        return task

    async def run_extraction(self, task_id: uuid.UUID) -> None:
        import asyncio
        
        task = self.db.get(ExtractionTask, task_id)
        if not task:
            return

        task.status = "PROCESSING"
        self.db.commit()

        items = (
            self.db.query(ExtractionItem)
            .filter(ExtractionItem.task_id == task_id, ExtractionItem.status == "PENDING")
            .all()
        )

        sem = asyncio.Semaphore(10)  # Limit concurrency to 10

        async def process_item(item):
            async with sem:
                try:
                    # Prepare text for LLM
                    text = json.dumps(item.original_data, ensure_ascii=False)
                    
                    extracted, usage = await self.client.extract_features_async(text, task.target_fields)
                    
                    if isinstance(extracted, dict):
                        extracted["_usage"] = usage
                    
                    item.extracted_data = extracted
                    item.status = "SUCCESS"
                except Exception as e:
                    item.status = "FAILED"
                    item.error_message = str(e)
                    logger.exception("特征提取失败：task_id=%s item_id=%s", task_id, item.id)

        # Create tasks for all items
        tasks = [process_item(item) for item in items]
        
        # Run in batches to allow intermediate commits (optional, but good for safety)
        # For simplicity and speed, we gather all, but maybe commit every N items?
        # Since we are modifying attached objects, we can just gather all and commit at the end.
        # However, for large lists, we might want to chunk.
        
        chunk_size = 50
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i : i + chunk_size]
            await asyncio.gather(*chunk)
            self.db.commit()

        task.status = "COMPLETED"
        self.db.commit()

    async def extract_batch_features(
        self, 
        batch_id: int, 
        target_fields: List[str],
        custom_instructions: str | None = None,
        test_mode: bool = False
    ) -> None:
        import asyncio
        from datetime import datetime, timezone
        from app.models.import_batch import ProductRecord, ImportBatch
        from app.models.extraction_run import ExtractionRun

        # Pricing constants (DeepSeek V3)
        PRICE_PER_1M_INPUT = 0.14
        PRICE_PER_1M_OUTPUT = 0.28

        start_time = datetime.now(timezone.utc)

        # Create ExtractionRun
        run = ExtractionRun(
            batch_id=batch_id,
            status="processing",
            target_fields=target_fields,
            created_at=start_time
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        # Update batch status to processing (optional, just to show activity)
        # Only update batch status if it's a full run
        batch = self.db.get(ImportBatch, batch_id)
        if batch and not test_mode:
            batch.ai_status = "processing"
            self.db.commit()

        records = (
            self.db.query(ProductRecord)
            .filter(ProductRecord.batch_id == batch_id)
            .all()
        )
        
        # If test mode, only take first 3 records
        if test_mode:
            records = records[:3]
        
        if not records:
            run.status = "completed"
            run.stats = {"total": 0, "success": 0, "failed": 0}
            run.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            
            if batch and not test_mode:
                batch.ai_status = "completed"
                self.db.commit()
            return

        sem = asyncio.Semaphore(10)
        
        stats = {
            "success": 0, 
            "failed": 0,
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0
        }

        async def process_record(record):
            async with sem:
                try:
                    # Use raw_payload to ensure we have all fields (like description, bullets)
                    # normalized_payload might be a subset of clean data
                    data = record.raw_payload or record.normalized_payload
                    # Prepare text for LLM
                    text = json.dumps(data, ensure_ascii=False)
                    
                    extracted, usage = await self.client.extract_features_async(
                        text, 
                        target_fields,
                        custom_instructions=custom_instructions
                    )
                    
                    if isinstance(extracted, dict):
                        extracted["_usage"] = usage
                        # Accumulate tokens
                        if usage:
                            input_t = usage.get("prompt_tokens", 0)
                            output_t = usage.get("completion_tokens", 0)
                            stats["input_tokens"] += input_t
                            stats["output_tokens"] += output_t
                            stats["total_tokens"] += (input_t + output_t)

                    # If test mode, we might not want to overwrite the main record's ai_features
                    # But for now, let's overwrite so the user can see it in the UI easily.
                    # Or maybe we should store it in the run? 
                    # The current UI reads from record.ai_features.
                    # Let's overwrite. It's a "Test Run" on the data.
                    record.ai_features = extracted
                    record.ai_status = "success"
                    stats["success"] += 1
                except Exception:
                    record.ai_status = "failed"
                    stats["failed"] += 1
                    logger.exception("批次特征提取失败：batch_id=%s record_id=%s", batch_id, record.id)

        tasks = [process_record(record) for record in records]
        
        chunk_size = 50
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i : i + chunk_size]
            await asyncio.gather(*chunk)
            self.db.commit()
            
        # Update batch status to completed
        if batch and not test_mode:
            self.db.refresh(batch)
            # Calculate cost
            input_cost = (stats["input_tokens"] / 1_000_000) * PRICE_PER_1M_INPUT
            output_cost = (stats["output_tokens"] / 1_000_000) * PRICE_PER_1M_OUTPUT
            total_cost = input_cost + output_cost
            
            # Update Batch status
            batch.ai_status = "completed"
            self.db.commit()

        # Update Run
        end_time = datetime.now(timezone.utc)
        duration_seconds = (end_time - start_time).total_seconds()
        
        # Calculate cost for the run
        input_cost = (stats["input_tokens"] / 1_000_000) * PRICE_PER_1M_INPUT
        output_cost = (stats["output_tokens"] / 1_000_000) * PRICE_PER_1M_OUTPUT
        total_cost = input_cost + output_cost

        run.status = "completed"
        run.finished_at = end_time
        run.stats = {
            "total": len(records),
            "success": stats["success"],
            "failed": stats["failed"],
            "total_tokens": stats["total_tokens"],
            "input_tokens": stats["input_tokens"],
            "output_tokens": stats["output_tokens"],
            "total_cost": round(total_cost, 6),
            "duration_seconds": round(duration_seconds, 2)
        }
        self.db.commit()

    def list_tasks(self, limit: int = 20, offset: int = 0) -> List[ExtractionTask]:
        """获取任务列表,按创建时间倒序"""
        return (
            self.db.query(ExtractionTask)
            .order_by(ExtractionTask.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_task(self, task_id: uuid.UUID) -> ExtractionTask | None:
        return self.db.get(ExtractionTask, task_id)

    def export_task(self, task_id: uuid.UUID) -> io.BytesIO:
        if pd is None:
            raise ImportError("Pandas is not installed.")
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found")

        items = self.db.query(ExtractionItem).filter(ExtractionItem.task_id == task_id).all()

        data = []
        if not items:
            return io.BytesIO()

        for item in items:
            row = item.original_data.copy()
            if item.extracted_data:
                row.update(item.extracted_data)
            data.append(row)

        df = pd.DataFrame(data)

        # Reorder columns: ASIN and Title first, then original, then target fields
        priority_keywords = ["asin", "title", "标题", "product_name", "bullet", "五点"]
        priority_cols = []
        
        # Find all columns that match priority keywords (case-insensitive)
        for col in df.columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in priority_keywords):
                priority_cols.append(col)
        
        # Sort priority_cols to put ASIN before Title if both exist
        priority_cols.sort(key=lambda x: (0 if "asin" in x.lower() else 1))

        # Construct final column order
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[priority_cols + other_cols]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return output

    async def auto_translate_batch(self, batch_id: int) -> None:
        """
        自动翻译批次中的产品信息（标题和五点）
        """
        import asyncio
        from app.models.import_batch import ProductRecord
        
        records = (
            self.db.query(ProductRecord)
            .filter(ProductRecord.batch_id == batch_id)
            .all()
        )
        
        if not records:
            return

        sem = asyncio.Semaphore(10)
        
        async def process_record(record):
            async with sem:
                try:
                    # Construct text from raw_payload
                    payload = record.raw_payload or {}
                    # Try to find title and bullets from common keys
                    title = payload.get("Title") or payload.get("title") or payload.get("标题") or ""
                    bullets = payload.get("Bullet Points") or payload.get("bullet_points") or payload.get("五点描述") or ""
                    
                    if not title and not bullets:
                        return

                    text = f"Title: {title}\nBullets: {bullets}"
                    
                    translated, _ = await self.client.translate_product_info_async(text)
                    
                    if translated:
                        # Update raw_payload with new fields
                        # We need to clone it to trigger SQLAlchemy change detection if it's a mutable dict, 
                        # or just assign a new dict.
                        new_payload = dict(payload)
                        if "title_cn" in translated:
                            new_payload["title_cn"] = translated["title_cn"]
                        if "bullets_cn" in translated:
                            new_payload["bullets_cn"] = translated["bullets_cn"]
                        
                        record.raw_payload = new_payload
                        
                except Exception:
                    logger.exception("自动翻译失败：batch_id=%s record_id=%s", batch_id, record.id)

        tasks = [process_record(record) for record in records]
        
        chunk_size = 50
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i : i + chunk_size]
            await asyncio.gather(*chunk)
            self.db.commit()
