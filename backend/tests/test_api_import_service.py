"""
单元测试：API 导入服务

测试 API 导入功能的核心逻辑
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.api_import_service import APIImportService
from app.config import settings

class TestAPIImportService:
    """测试 API 导入服务"""
    
    def test_parse_input_category_id(self):
        """测试解析类目 ID"""
        service = APIImportService()
        
        # 测试纯数字输入
        result = service._parse_input("172282")
        assert result["type"] == "category_id"
        assert result["value"] == "172282"
        assert result["category_id"] == "172282"
    
    def test_default_config(self):
        """测试默认配置"""
        service = APIImportService()
        
        assert service.default_test_batch_size == 10
    
    @pytest.mark.asyncio
    async def test_fetch_bestsellers_mock(self):
        """测试获取 Best Sellers（模拟）"""
        service = APIImportService()
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.code = 0
        mock_response.data = {
            "products": [
                {"asin": f"B0{i:08d}", "title": f"Product {i}"}
                for i in range(100)
            ]
        }
        
        # Mock settings.sorftime_api_key
        with patch('app.config.settings.sorftime_api_key', 'test_key'):
            with patch('app.services.api_import_service.SorftimeClient') as MockClient:
                mock_client = AsyncMock()
                mock_client.category_request.return_value = mock_response
                MockClient.return_value = mock_client
                
                result = await service._fetch_bestsellers("172282", 1)
                
                assert len(result) == 100
                assert result[0]["asin"] == "B000000000"
    
    @pytest.mark.asyncio
    async def test_fetch_details_batch_mock(self):
        """测试批量获取详情（模拟）"""
        service = APIImportService()
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.code = 0
        mock_response.data = {
            "products": [
                {
                    "asin": f"B0{i:08d}",
                    "title": f"Product {i}",
                    "price": 99.99,
                    "ratings": 4.5,
                    "ratingsCount": 1000,
                }
                for i in range(10)
            ]
        }
        
        # Mock settings.sorftime_api_key
        with patch('app.config.settings.sorftime_api_key', 'test_key'):
            with patch('app.services.api_import_service.SorftimeClient') as MockClient:
                mock_client = AsyncMock()
                mock_client.product_request.return_value = mock_response
                MockClient.return_value = mock_client
                
                asins = [f"B0{i:08d}" for i in range(10)]
                result = await service._fetch_details_batch(asins, 1)
                
                assert len(result) == 10
                assert result[0]["asin"] == "B000000000"
                assert result[0]["price"] == 99.99


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
