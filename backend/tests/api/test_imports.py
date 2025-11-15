from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_import_file_success() -> None:
    sample_file = DATA_DIR / "sorftime-demo.csv"
    with sample_file.open("rb") as f:
        response = client.post(
            "/imports",
            files={"file": (sample_file.name, f, "text/csv")},
            data={"importStrategy": "append"},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] in {"pending", "running", "succeeded"}


def test_import_file_validation_error() -> None:
    response = client.post(
        "/imports",
        files={},
        data={"importStrategy": "append"},
    )
    assert response.status_code == 400
