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
def test_summarize_api_error(client):
    # Mock 500 error
    respx.post("https://api.deepseek.com/chat/completions").mock(
        return_value=Response(500, json={"error": "Server Error"})
    )

    result = client.summarize("test question", {})
    
    # Should return fallback answer, not raise exception
    # 错误消息可能变化,只检查返回了结果
    assert "answer" in result
    assert "AI 服务暂时不可用" in result["answer"]


def test_no_api_key():
    with patch.dict(os.environ, {}, clear=True):
        client = DeepseekClient()
        result = client.summarize("test", {})
        assert "离线模式" in result["answer"]
        assert result["trace"]["mode"] == "fallback"
