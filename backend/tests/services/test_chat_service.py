from unittest.mock import MagicMock, patch

import pytest

from app.services.chat_service import ChatService
from app.services.chat_tools import query_products, get_batch_status
from app.models import ImportBatch, ProductRecord

@pytest.fixture
def mock_deepseek():
    with patch("app.services.chat_service.DeepseekClient") as MockClient:
        instance = MockClient.return_value
        yield instance

@pytest.fixture
def chat_service(mock_deepseek):
    return ChatService(client=mock_deepseek)

def test_ask_direct_message(chat_service, mock_deepseek, db):
    # Mock intent recognition to return a direct message
    mock_deepseek.chat.return_value = {
        "content": "Hello",
        "trace": {"usage": 10}
    }
    mock_deepseek.parse_json_response.return_value = {
        "type": "message",
        "content": "Hello User"
    }

    result = chat_service.ask(db, question="Hi")

    assert result["answer"] == "Hello User"
    assert result["session_id"] is not None
    # Verify chat was called once
    mock_deepseek.chat.assert_called_once()

def test_ask_tool_call_flow(chat_service, mock_deepseek, db):
    # 1. Mock intent recognition to return a tool call
    mock_deepseek.chat.side_effect = [
        # First call: Intent recognition
        {
            "content": '{"type": "tool_call", "tool": "query_products", "params": {"keyword": "phone"}}',
            "trace": {"step": 1}
        },
        # Second call: Final answer generation
        {
            "content": "Here are the phones I found.",
            "trace": {"step": 2}
        }
    ]
    
    # Mock parse_json_response for the first call
    mock_deepseek.parse_json_response.side_effect = [
        {"type": "tool_call", "tool": "query_products", "params": {"keyword": "phone"}},
        None # Should not be called second time, but just in case
    ]

    # Mock ToolRegistry to return our mock tool or use real one if we mock DB data
    # Let's mock the tool execution to avoid DB dependency in this unit test
    with patch("app.services.chat_service.ToolRegistry.get_tool") as mock_get_tool:
        mock_tool_func = MagicMock(return_value=[{"asin": "123", "title": "Test Phone"}])
        mock_get_tool.return_value = mock_tool_func

        result = chat_service.ask(db, question="Find phones")

        assert result["answer"] == "Here are the phones I found."
        assert len(result["references"]) == 1
        assert result["references"][0]["data"]["asin"] == "123"
        
        # Verify tool was called
        mock_get_tool.assert_called_with("query_products")
        mock_tool_func.assert_called_with(db, keyword="phone")
        
        # Verify chat was called twice
        assert mock_deepseek.chat.call_count == 2

def test_ask_tool_execution_error(chat_service, mock_deepseek, db):
    # Mock intent to call a tool that fails
    mock_deepseek.chat.return_value = {
        "content": "tool call",
        "trace": {}
    }
    mock_deepseek.parse_json_response.return_value = {
        "type": "tool_call", 
        "tool": "query_products", 
        "params": {}
    }

    with patch("app.services.chat_service.ToolRegistry.get_tool") as mock_get_tool:
        mock_tool_func = MagicMock(side_effect=Exception("DB Error"))
        mock_get_tool.return_value = mock_tool_func

        result = chat_service.ask(db, question="Find phones")

        # Should return error message as answer
        assert "执行查询时发生错误" in result["answer"]
        assert "DB Error" in result["answer"]

def test_tool_query_products(db):
    # Prepare data
    batch = ImportBatch(
        id=1, 
        status="succeeded", 
        total_rows=1, 
        success_rows=1, 
        failed_rows=0,
        filename="test.csv",
        storage_path="/tmp/test.csv",
        import_strategy="append"
    )
    db.add(batch)
    product = ProductRecord(batch_id=1, asin="B001", title="Test Product", price=10.0)
    db.add(product)
    db.commit()

    # Test tool
    results = query_products(db, keyword="B001")
    assert len(results) == 1
    assert results[0]["asin"] == "B001"
    assert results[0]["title"] == "Test Product"

def test_tool_get_batch_status(db):
    # Prepare data
    batch = ImportBatch(
        id=123, 
        status="succeeded", 
        filename="test.csv",
        storage_path="/tmp/test.csv",
        import_strategy="append"
    )
    db.add(batch)
    db.commit()

    # Test tool
    result = get_batch_status(db, batch_id=123)
    assert isinstance(result, dict)
    assert result["batch_id"] == 123
    assert result["status"] == "succeeded"

    # Test not found
    result = get_batch_status(db, batch_id=999)
    assert "未找到批次" in result
