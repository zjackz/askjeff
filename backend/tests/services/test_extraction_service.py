import asyncio
import io
import json
from unittest.mock import MagicMock, patch, AsyncMock

import pandas as pd
import pytest
from fastapi import UploadFile

from app.services.extraction_service import ExtractionService
from app.models import ImportBatch, ProductRecord, ExtractionTask, ExtractionItem

@pytest.fixture
def mock_deepseek():
    with patch("app.services.extraction_service.DeepseekClient") as MockClient:
        instance = MockClient.return_value
        instance.extract_features_async = AsyncMock(return_value=({"Color": "Red"}, {"prompt_tokens": 10, "completion_tokens": 5}))
        yield instance

@pytest.fixture
def extraction_service(db, mock_deepseek):
    return ExtractionService(db, mock_deepseek)

@pytest.mark.asyncio
async def test_create_task_csv(extraction_service, db):
    content = b"Product Name,Description\nPhone,A smartphone"
    file = UploadFile(filename="test.csv", file=io.BytesIO(content))
    
    task = await extraction_service.create_task(file, target_fields=["Color"])
    
    assert task.filename == "test.csv"
    assert task.status == "PENDING"
    assert len(task.target_fields) == 1
    
    # Verify items created
    items = db.query(ExtractionItem).filter(ExtractionItem.task_id == task.id).all()
    assert len(items) == 1
    assert items[0].original_data["Product Name"] == "Phone"

@pytest.mark.asyncio
async def test_create_task_excel(extraction_service, db):
    df = pd.DataFrame([{"Product Name": "Laptop", "Description": "A laptop"}])
    content = io.BytesIO()
    with pd.ExcelWriter(content, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    content.seek(0)
    
    file = UploadFile(filename="test.xlsx", file=content)
    
    task = await extraction_service.create_task(file, target_fields=["CPU"])
    
    assert task.filename == "test.xlsx"
    
    items = db.query(ExtractionItem).filter(ExtractionItem.task_id == task.id).all()
    assert len(items) == 1

@pytest.mark.asyncio
async def test_extract_batch_features(extraction_service, db, mock_deepseek):
    # Prepare data
    batch = ImportBatch(
        status="succeeded", 
        filename="test.csv", 
        storage_path="/tmp/test.csv",
        import_strategy="append"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    record = ProductRecord(
        batch_id=batch.id, 
        asin="B001", 
        title="Test Product", 
        raw_payload={"title": "Test Product", "description": "Red Phone"}
    )
    db.add(record)
    db.commit()
    
    # Run extraction
    await extraction_service.extract_batch_features(batch.id, target_fields=["Color"])
    
    # Verify
    db.refresh(record)
    assert record.ai_status == "success"
    assert record.ai_features == {"Color": "Red", "_usage": {"prompt_tokens": 10, "completion_tokens": 5}}
    
    db.refresh(batch)
    assert batch.ai_status == "completed"
    
    # Verify ExtractionRun created
    assert len(batch.extraction_runs) == 1
    run = batch.extraction_runs[0]
    assert run.status == "completed"
    assert run.stats["success"] == 1
    assert run.stats["total_tokens"] == 15

@pytest.mark.asyncio
async def test_extract_batch_features_empty(extraction_service, db):
    # Prepare batch with no records
    batch = ImportBatch(
        status="succeeded", 
        filename="empty.csv", 
        storage_path="/tmp/empty.csv",
        import_strategy="append"
    )
    db.add(batch)
    db.commit()
    
    await extraction_service.extract_batch_features(batch.id, target_fields=["Color"])
    
    db.refresh(batch)
    assert batch.ai_status == "completed"
    assert len(batch.extraction_runs) == 1
    assert batch.extraction_runs[0].stats["total"] == 0

@pytest.mark.asyncio
async def test_extract_batch_features_error(extraction_service, db, mock_deepseek):
    # Mock error
    mock_deepseek.extract_features_async.side_effect = Exception("API Error")
    
    # Prepare data
    batch = ImportBatch(
        status="succeeded", 
        filename="test.csv", 
        storage_path="/tmp/test.csv",
        import_strategy="append"
    )
    db.add(batch)
    db.commit()
    
    record = ProductRecord(
        batch_id=batch.id, 
        asin="B002", 
        title="Error Product", 
        raw_payload={"title": "Error Product"}
    )
    db.add(record)
    db.commit()
    
    await extraction_service.extract_batch_features(batch.id, target_fields=["Color"])
    
    db.refresh(record)
    assert record.ai_status == "failed"
    
    db.refresh(batch)
    assert batch.ai_status == "completed" # Batch completes even if items fail
    
    run = batch.extraction_runs[0]
    assert run.stats["failed"] == 1
