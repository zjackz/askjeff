import pytest
from unittest.mock import AsyncMock, patch
from app.services.ads_ai_service import AdsAIService

@pytest.fixture
def ai_service():
    return AdsAIService()

@pytest.mark.asyncio
async def test_generate_sku_diagnosis_success(ai_service):
    # Mock DeepSeekClient
    with patch.object(ai_service.client, 'analyze_with_system_prompt', new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = "AI Diagnosis Result"
        
        metrics = {
            "stock_weeks": 10,
            "tacos": 15,
            "acos": 25,
            "ctr": 1.2,
            "cvr": 10,
            "margin": 20,
            "sales": 1000
        }
        
        result = await ai_service.generate_sku_diagnosis("TEST-SKU", metrics)
        
        assert result == "AI Diagnosis Result"
        mock_analyze.assert_called_once()
        # Verify SKU is in the prompt
        args, kwargs = mock_analyze.call_args
        assert "TEST-SKU" in kwargs['user_prompt']

@pytest.mark.asyncio
async def test_generate_sku_diagnosis_failure(ai_service):
    # Mock DeepSeekClient to raise exception
    with patch.object(ai_service.client, 'analyze_with_system_prompt', side_effect=Exception("API Error")):
        metrics = {"stock_weeks": 10}
        result = await ai_service.generate_sku_diagnosis("TEST-SKU", metrics)
        
        assert "【AI 诊断暂时不可用】" in result

@pytest.mark.asyncio
async def test_generate_store_strategy_success(ai_service):
    with patch.object(ai_service.client, 'analyze_with_system_prompt', new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = "Store Strategy Result"
        
        overview = {
            "health_score": 85,
            "total_sales": 50000,
            "tacos": 12,
            "quadrant_distribution": {"Star": 5}
        }
        
        result = await ai_service.generate_store_strategy(overview)
        
        assert result == "Store Strategy Result"
        mock_analyze.assert_called_once()
