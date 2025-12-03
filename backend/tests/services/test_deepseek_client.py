import os
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from app.services.deepseek_client import DeepseekClient


@pytest.fixture
def client():
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
        yield DeepseekClient()


@respx.mock
def test_summarize_success(client):
    # Mock DeepSeek API response
    respx.post("https://api.deepseek.com/chat/completions").mock(
        return_value=Response(
            200,
            json={
                "choices": [{"message": {"content": "Mocked Answer"}}],
                "usage": {"total_tokens": 10},
            },
        )
    )

    result = client.summarize("test question", {"context": "data"})
    
    assert result["answer"] == "Mocked Answer"
    assert result["trace"]["usage"]["total_tokens"] == 10


@respx.mock
def test_summarize_api_error(): # Removed client fixture as it's instantiated inside
    # 模拟 API 错误响应
    respx.post(f"{settings.deepseek_base_url}/chat/completions").mock(
        return_value=httpx.Response(
            status_code=500,
            json={"error": {"message": "Internal server error"}},
        )
    )
    
    client = DeepseekClient()
    with pytest.raises(Exception) as exc_info:
        client.summarize("test content")
    
    # 验证错误被正确抛出(不检查具体消息,因为可能变化)
    assert exc_info.value is not None # Corrected assertion
    assert "Internal server error" in str(exc_info.value) # Added assertion to check error message content


def test_no_api_key():
    with patch.dict(os.environ, {}, clear=True):
        client = DeepseekClient()
        result = client.summarize("test", {})
        assert "离线模式" in result["answer"]
        assert result["trace"]["mode"] == "fallback"
