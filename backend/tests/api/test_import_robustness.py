from __future__ import annotations
# import pytest # Unused
from fastapi.testclient import TestClient
from app.main import app
# from app.services.import_service import ImportAbort # Unused

client = TestClient(app)

def test_import_gbk_csv_success() -> None:
    """Test importing a CSV file encoded in GBK (should succeed now)."""
    # Create GBK encoded content
    content = "asin,title,currency\nB001,中文标题,USD\n".encode("gbk")
    
    response = client.post(
        "/api/imports",
        files={"file": ("gbk.csv", content, "text/csv")},
        data={"importStrategy": "append"},
    )
    assert response.status_code == 201
    batch = response.json()
    assert batch["status"] == "succeeded"

def test_import_excel_fallback_success() -> None:
    """Test importing an Excel file with a non-default sheet name (should fallback if single sheet)."""
    import openpyxl
    from io import BytesIO
    
    # Create Excel file with "Sheet1" instead of "产品详情"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["asin", "title", "currency"])
    ws.append(["B002", "Test Product", "USD"])
    
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    
    response = client.post(
        "/api/imports",
        files={"file": ("wrong_sheet.xlsx", bio.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"importStrategy": "append"},
    )
    
    assert response.status_code == 201
    batch = response.json()
    assert batch["status"] == "succeeded"
