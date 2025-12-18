# import pytest (moved or removed)
from app.services.api_import_service import APIImportService

def test_parse_input_asin():
    service = APIImportService()
    
    # Pure ASIN
    result = service._parse_input("B0C1S6Z7Y2")
    assert result["type"] == "asin"
    assert result["value"] == "B0C1S6Z7Y2"
    
    # URL with ASIN
    result = service._parse_input("https://www.amazon.com/dp/B0C1S6Z7Y2")
    assert result["type"] == "asin"
    assert result["value"] == "B0C1S6Z7Y2"
    
    # URL with ASIN and parameters
    result = service._parse_input("https://www.amazon.com/dp/B0C1S6Z7Y2?ref=nav_youraccount_switchacct")
    assert result["type"] == "asin"
    assert result["value"] == "B0C1S6Z7Y2"

def test_parse_input_category():
    service = APIImportService()
    
    # Pure Category ID
    result = service._parse_input("172282")
    assert result["type"] == "category_id"
    assert result["value"] == "172282"
    
    # URL with node parameter
    result = service._parse_input("https://www.amazon.com/b?node=172282")
    assert result["type"] == "category_id"
    assert result["value"] == "172282"
    
    # Best Sellers URL
    result = service._parse_input("https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/172282")
    assert result["type"] == "category_id"
    assert result["value"] == "172282"

def test_parse_input_invalid():
    service = APIImportService()
    try:
        service._parse_input("invalid string")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "无法识别的输入格式" in str(e)
if __name__ == "__main__":
    import sys
    import os
    # Add backend to path
    sys.path.append(os.path.join(os.getcwd(), "backend"))
    
    try:
        import pytest
        sys.exit(pytest.main([__file__]))
    except ImportError:
        print("Pytest not found, running manually...")
        service = APIImportService()
        test_parse_input_asin()
        test_parse_input_category()
        print("All tests passed!")
