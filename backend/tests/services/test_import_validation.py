import io
import pytest
from fastapi import UploadFile
from app.services.import_service import import_service
from app.models.import_batch import ImportBatch, ProductRecord

def create_upload_file(content: bytes, filename: str) -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(content))

def test_duplicate_file_upload(db):
    content = b"ASIN,Title,Price\nB000000001,Test Product,10.0"
    file1 = create_upload_file(content, "test.csv")
    
    # First upload
    batch1 = import_service.handle_upload(
        db, 
        file=file1, 
        import_strategy="append"
    )
    assert batch1.status == "succeeded"
    assert batch1.file_hash is not None

    # Second upload (same content)
    file2 = create_upload_file(content, "test_dup.csv")
    with pytest.raises(ValueError, match="检测到重复文件导入"):
        import_service.handle_upload(
            db, 
            file=file2, 
            import_strategy="append"
        )

def test_asin_validation(db):
    # Invalid ASIN (too short)
    content = b"ASIN,Title,Price\nINVALID,Test Product,10.0"
    file = create_upload_file(content, "invalid_asin.csv")
    
    batch = import_service.handle_upload(
        db, 
        file=file, 
        import_strategy="append"
    )
    
    assert batch.status == "succeeded" # Import succeeds but with warnings
    
    records = db.query(ProductRecord).filter(ProductRecord.batch_id == batch.id).all()
    assert len(records) == 1
    record = records[0]
    
    assert record.validation_status == "warning"
    assert "asin" in record.validation_messages
    assert "ASIN 格式不正确" in record.validation_messages["asin"]

def test_valid_asin(db):
    # Valid ASIN
    content = b"ASIN,Title,Price\nB012345678,Test Product,10.0"
    file = create_upload_file(content, "valid_asin.csv")
    
    batch = import_service.handle_upload(
        db, 
        file=file, 
        import_strategy="append"
    )
    
    records = db.query(ProductRecord).filter(ProductRecord.batch_id == batch.id).all()
    assert len(records) == 1
    assert records[0].validation_status == "valid"
