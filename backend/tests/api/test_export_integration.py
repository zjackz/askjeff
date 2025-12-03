from __future__ import annotations
import csv
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_export_integration() -> None:
    """Test the full export flow: Import -> Export -> Download -> Verify."""
    
    # 1. Setup: Import some data
    # We can use the import_service directly or just insert data into DB.
    # Using import_service is more realistic but requires a file.
    # Let's insert data directly into DB for simplicity and speed, 
    # or use the import endpoint if we want to test that too (but we already did).
    # Actually, let's use the import endpoint to be sure we have a valid batch.
    
    # Create a dummy CSV
    content = "asin,title,currency,price,validation_status\nB001,Test Product 1,USD,10.00,valid\nB002,Test Product 2,USD,20.00,valid\n".encode("utf-8")
    
    import_response = client.post(
        "/api/imports",
        files={"file": ("export_test.csv", content, "text/csv")},
        data={"importStrategy": "append"},
    )
    assert import_response.status_code == 201
    batch_id = import_response.json()["id"]
    
    # 2. Trigger Export
    export_payload = {
        "exportType": "clean-products",
        "filters": {"batch_id": batch_id},
        "selectedFields": ["asin", "title", "price"],
        "fileFormat": "csv"
    }
    
    export_response = client.post("/api/exports", json=export_payload)
    assert export_response.status_code == 202
    job_data = export_response.json()
    job_id = job_data["id"]
    
    # 3. Check Job Status (it runs synchronously in the current implementation for simplicity, 
    # but let's poll just in case or check the returned status)
    # The current implementation in export_service.create_job runs _generate_file immediately inside the try block.
    # So it should be "succeeded" immediately.
    
    get_job_response = client.get(f"/api/exports/{job_id}")
    assert get_job_response.status_code == 200
    job_status = get_job_response.json()
    assert job_status["status"] == "succeeded"
    
    # 4. Download File
    download_response = client.get(f"/api/exports/{job_id}/download")
    assert download_response.status_code == 200
    
    # 5. Verify Content
    decoded_content = download_response.content.decode("utf-8")
    reader = csv.DictReader(decoded_content.splitlines())
    rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]["asin"] == "B001"
    assert rows[0]["title"] == "Test Product 1"
    assert rows[0]["price"] == "10.00"
    assert rows[1]["asin"] == "B002"
    
    # Clean up (optional, but good practice if using real DB)
    # In this environment, we might be using a persistent DB, so maybe we should leave it or clean it.
    # The tests usually run in a transaction or a separate DB. 
    # Given the makefile uses `poetry run pytest`, it likely uses the dev DB or a test DB.
    # We won't explicitly clean up here to keep it simple, assuming test isolation or ephemeral DB.
