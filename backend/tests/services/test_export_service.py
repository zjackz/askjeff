import pytest
from unittest.mock import MagicMock, patch
from app.services.export_service import export_service
from app.models import ExportJob, ProductRecord, ExtractionRun

def test_export_invalid_type(db):
    """Test exporting with an invalid export type."""
    with pytest.raises(ValueError, match="不支持的导出类型"):
        export_service.create_job(
            db,
            export_type="invalid_type",
            filters={},
            selected_fields=["asin"],
            file_format="csv"
        )

def test_export_invalid_format(db):
    """Test exporting with an invalid file format."""
    with pytest.raises(ValueError, match="不支持的导出文件格式"):
        export_service.create_job(
            db,
            export_type="clean_products",
            filters={},
            selected_fields=["asin"],
            file_format="txt"
        )

def test_export_no_fields_selected(db):
    """Test exporting without selecting any fields (for non-extraction types)."""
    with pytest.raises(ValueError, match="请选择至少一个允许导出的字段"):
        export_service.create_job(
            db,
            export_type="clean_products",
            filters={},
            selected_fields=[],
            file_format="csv"
        )

def test_export_empty_dataset(db):
    """Test exporting when no data matches the filters."""
    # Ensure no data exists
    db.query(ProductRecord).delete()
    db.commit()

    job = export_service.create_job(
        db,
        export_type="clean_products",
        filters={"batch_id": 99999}, # Non-existent batch
        selected_fields=["asin", "title"],
        file_format="csv"
    )
    
    assert job.status == "succeeded"
    assert job.file_path is not None
    # Verify file content is just header
    with open(job.file_path, "r") as f:
        content = f.read()
        assert "asin,title" in content
        assert len(content.splitlines()) == 1

def test_export_extraction_results_no_run_id(db):
    """Test exporting extraction results without providing run_id."""
    with pytest.raises(ValueError, match="导出提取结果需要指定 run_id"):
        export_service._fetch_extraction_rows(db, filters={})

def test_export_extraction_results_invalid_run_id(db):
    """Test exporting extraction results with a non-existent run_id."""
    with pytest.raises(ValueError, match="找不到指定的提取记录"):
        export_service._fetch_extraction_rows(db, filters={"run_id": 99999})
