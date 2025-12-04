import asyncio
import io
from unittest.mock import patch, AsyncMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_deepseek():
    with patch("app.api.routes.extraction.DeepseekClient") as MockClient:
        instance = MockClient.return_value
        # Mock extract_features_async to return dummy data (async)
        instance.extract_features_async = AsyncMock(return_value=({"电池容量": "5000mAh", "材质": "铝合金"}, {"total_tokens": 10}))
        yield instance


def test_extraction_flow(mock_deepseek):
    """
    Test the full extraction flow:
    1. Upload file
    2. Start extraction
    3. Check status
    4. Export result
    """
    # 1. Create a dummy Excel file
    df = pd.DataFrame([
        {"Product Name": "Phone A", "Description": "Battery 5000mAh, Metal body"},
        {"Product Name": "Phone B", "Description": "Battery 4000mAh, Plastic body"},
    ])
    file_content = io.BytesIO()
    with pd.ExcelWriter(file_content, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    file_content.seek(0)

    # 2. Upload File
    response = client.post(
        "/api/extraction/upload",
        files={"file": ("test_products.xlsx", file_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    assert response.status_code == 200
    task_data = response.json()
    task_id = task_data["id"]
    assert task_data["status"] == "PENDING"
    assert "Product Name" in task_data["columns"]

    # 3. Start Extraction
    # We mock the background task execution by running it synchronously or just trusting the mock
    # But since we use BackgroundTasks, TestClient usually doesn't run them automatically unless we trigger them.
    # For this integration test, we can mock the service method or force execution.
    # Let's just call the endpoint and verify it returns success.
    
    response = client.post(
        f"/api/extraction/{task_id}/start",
        json={"target_fields": ["电池容量", "材质"]}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Extraction started"

    # Since background tasks might not run in TestClient immediately/easily without setup,
    # let's manually trigger the processing logic to simulate "completion" for the sake of testing the export.
    # We can do this by importing the service and running it, or just updating the DB directly if we had DB access here.
    # A better way for integration test is to use the service directly to "run" the task.
    
    from app.db import SessionLocal
    from app.services.extraction_service import ExtractionService
    
    with SessionLocal() as db:
        service = ExtractionService(db, mock_deepseek)
        # Run async method synchronously
        asyncio.run(service.run_extraction(task_id))

    # 4. Check Status (should be COMPLETED now)
    response = client.get(f"/api/extraction/{task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

    # 5. Export Result
    response = client.get(f"/api/extraction/{task_id}/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Verify exported content
    exported_content = io.BytesIO(response.content)
    exported_df = pd.read_excel(exported_content)
    
    assert "电池容量" in exported_df.columns
    assert "材质" in exported_df.columns
    # Check if mock data was filled (first row)
    assert exported_df.iloc[0]["电池容量"] == "5000mAh"
