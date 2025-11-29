import io
import json
import uuid
from typing import List

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.extraction import ExtractionItem, ExtractionTask
from app.services.deepseek_client import DeepseekClient


class ExtractionService:
    def __init__(self, db: Session, client: DeepseekClient):
        self.db = db
        self.client = client

    async def create_task(self, file: UploadFile, target_fields: List[str] | None = None) -> ExtractionTask:
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

    def run_extraction(self, task_id: uuid.UUID) -> None:
        task = self.db.query(ExtractionTask).get(task_id)
        if not task:
            return

        task.status = "PROCESSING"
        self.db.commit()

        items = (
            self.db.query(ExtractionItem)
            .filter(ExtractionItem.task_id == task_id, ExtractionItem.status == "PENDING")
            .all()
        )

        for item in items:
            try:
                # Prepare text for LLM
                text = json.dumps(item.original_data, ensure_ascii=False)
                
                extracted = self.client.extract_features(text, task.target_fields)
                
                item.extracted_data = extracted
                item.status = "SUCCESS"
            except Exception as e:
                item.status = "FAILED"
                item.error_message = str(e)
            
            # Commit periodically could be better, but for now commit per item is safer for progress
            self.db.commit()

        task.status = "COMPLETED"
        self.db.commit()

    def get_task(self, task_id: uuid.UUID) -> ExtractionTask | None:
        return self.db.query(ExtractionTask).get(task_id)

    def export_task(self, task_id: uuid.UUID) -> io.BytesIO:
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

        # Reorder columns: Original + Target Fields
        # Get original columns from the first item if available
        original_cols = list(items[0].original_data.keys()) if items else []
        
        # Ensure target fields are present
        for field in task.target_fields:
            if field not in df.columns:
                df[field] = None
        
        # Construct final column order
        cols = original_cols + [f for f in task.target_fields if f not in original_cols]
        
        # Filter df to only include these columns (and any others that might have been added?)
        # Actually, let's just use the columns we have but ordered
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return output
