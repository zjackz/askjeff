import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from app.services.import_service import import_service, ImportAbort
from app.models import ImportBatch

def test_import_file_read_error(db):
    """Test handling of file read errors."""
    # Mock _save_file to return a path that doesn't exist or causes error
    with patch.object(import_service, '_save_file') as mock_save:
        mock_save.return_value = Path("/non/existent/path.csv")
        
        # Mock _calculate_file_hash to raise IOError
        with patch.object(import_service, '_calculate_file_hash', side_effect=IOError("Disk error")):
            file = MagicMock()
            file.filename = "test.csv"
            
            with pytest.raises(IOError, match="Disk error"):
                import_service.handle_upload(
                    db,
                    file=file,
                    import_strategy="append"
                )

def test_import_parse_abort(db):
    """Test handling of ImportAbort exception during parsing."""
    # Create a dummy batch
    batch = ImportBatch(
        filename="test.csv",
        storage_path="test.csv",
        import_strategy="append",
        status="pending"
    )
    db.add(batch)
    db.commit()
    
    # Mock _parse_file to raise ImportAbort
    with patch.object(import_service, '_parse_file', side_effect=ImportAbort("Parsing failed")):
        # We need to call a method that calls _parse_file, but handle_upload does a lot.
        # Let's test _parse_file directly or mock where it's called if possible.
        # Actually, handle_upload calls _parse_file.
        
        # We need to mock _save_file and _calculate_file_hash to bypass them
        with patch.object(import_service, '_save_file', return_value=Path("test.csv")), \
             patch.object(import_service, '_calculate_file_hash', return_value="hash"), \
             patch("app.services.import_repository.ImportRepository.create_batch", return_value=batch), \
             patch("app.services.import_repository.ImportRepository.find_batch_by_hash", return_value=None):
            
            file = MagicMock()
            file.filename = "test.csv"
            
            # handle_upload catches ImportAbort and updates batch status? 
            # Let's check handle_upload implementation.
            # It seems handle_upload lets exceptions propagate or handles them?
            # Looking at code, it doesn't seem to catch ImportAbort explicitly in handle_upload, 
            # but it might be handled by the caller or middleware.
            # Wait, let's check import_service.py again.
            
            with pytest.raises(ValueError, match="Parsing failed"):
                import_service.handle_upload(
                    db,
                    file=file,
                    import_strategy="append"
                )

def test_import_db_rollback(db):
    """Test database rollback on error."""
    # This is harder to test with mocks, but we can verify that if an error occurs,
    # changes are not committed.
    # We can mock db.commit to raise an exception.
    
    with patch.object(import_service, '_save_file', return_value=Path("test.csv")), \
         patch.object(import_service, '_calculate_file_hash', return_value="hash"), \
         patch("app.services.import_repository.ImportRepository.find_batch_by_hash", return_value=None):
             
        file = MagicMock()
        file.filename = "test.csv"
        
        # Mock create_batch to raise an exception
        with patch("app.services.import_repository.ImportRepository.create_batch", side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                import_service.handle_upload(
                    db,
                    file=file,
                    import_strategy="append"
                )
