from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_export(monkeypatch):
    mock_job = MagicMock()
    mock_job.id = "job123"
    mock_job.export_type = "clean_products"
    mock_job.status = "succeeded"
    mock_job.file_format = "csv"
    mock_job.filters = {"batch_id": "b1"}
    mock_job.selected_fields = ["asin"]
    mock_job.file_path = "/tmp/a.csv"
    mock_job.triggered_by = None
    mock_job.started_at = None
    mock_job.finished_at = None
    mock_job.error_message = None

    from app.services import export_service as service_module

    monkeypatch.setattr(service_module, "export_service", MagicMock(create_job=lambda *args, **kwargs: mock_job, get_job=lambda *args, **kwargs: mock_job))

    response = client.post(
        "/exports",
        json={
            "exportType": "clean_products",
            "filters": {"batch_id": "b1"},
            "selectedFields": ["asin"],
            "fileFormat": "csv",
        },
    )
    assert response.status_code == 202
    assert response.json()["id"] == "job123"
