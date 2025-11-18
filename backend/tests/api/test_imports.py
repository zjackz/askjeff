from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_import_file_success() -> None:
    sample_file = DATA_DIR / "吸尘器-sample.xlsx"
    with sample_file.open("rb") as f:
        response = client.post(
            "/imports",
            files={"file": (sample_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"importStrategy": "append"},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "succeeded"
    assert body["importStrategy"] == "append"
    assert body["totalRows"] == 100
    assert body["failedRows"] == 0


def test_import_file_with_failure_and_detail() -> None:
    # Python 的 bytes 字面量不支持非 ASCII 字符，这里改为字符串再以 UTF-8 编码
    bad_content = "asin,title,currency\n,缺少asin,USD\nB003,正常行,USD\n".encode("utf-8")
    response = client.post(
        "/imports",
        files={"file": ("broken.csv", bad_content, "text/csv")},
        data={"importStrategy": "update-only"},
    )
    assert response.status_code == 201
    batch = response.json()
    assert batch["status"] == "failed"
    detail = client.get(f"/imports/{batch['id']}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["failedRows"][0]["rowNumber"] == 2
    assert detail_body["failedRows"][0]["reason"] == "缺少必填字段: asin"


def test_product_list_after_import() -> None:
    sample_file = DATA_DIR / "吸尘器-sample.xlsx"
    with sample_file.open("rb") as f:
        response = client.post(
            "/imports",
            files={"file": (sample_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"importStrategy": "append"},
        )
    batch_id = response.json()["id"]

    products = client.get("/products", params={"batchId": batch_id})
    assert products.status_code == 200
    body = products.json()
    assert body["total"] == 100
    assert len(body["items"]) == 100


def test_import_file_validation_error() -> None:
    response = client.post(
        "/imports",
        files={},
        data={"importStrategy": "append"},
    )
    assert response.status_code == 400
