import sys
import os
import json
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from app.services.chat_service import chat_service, ToolRegistry
from app.services.deepseek_client import DeepseekClient

def test_chat_flow():
    print("Starting ChatService Flow Test...")

    # Mock Client
    mock_client = MagicMock(spec=DeepseekClient)
    # Save original client
    original_client = chat_service.client
    chat_service.client = mock_client

    # Mock DB Session
    mock_db = MagicMock()

    # --- Scenario 1: Tool Call (query_products) ---
    print("\nScenario 1: Tool Call (query_products)")
    
    # Mock responses for two rounds of chat
    mock_client.chat.side_effect = [
        # Round 1: Intent Recognition -> Returns JSON for tool call
        {
            "content": json.dumps({
                "type": "tool_call",
                "tool": "query_products",
                "params": {"limit": 2}
            }), 
            "trace": {"step": "intent"}
        },
        # Round 2: Final Answer -> Returns natural language
        {
            "content": "为您查询到 2 个产品：Test Product 1 和 Test Product 2。", 
            "trace": {"step": "final"}
        }
    ]

    # Mock Tool Execution
    # We hijack ToolRegistry.get_tool_func to return a mock function
    original_get_tool = ToolRegistry.get_tool_func
    
    def mock_tool_func(db, **kwargs):
        print(f"  [Mock] Executing tool with params: {kwargs}")
        return [
            {"asin": "B001", "title": "Test Product 1", "price": "10.00"},
            {"asin": "B002", "title": "Test Product 2", "price": "20.00"}
        ]

    def side_effect_get_tool(name):
        if name == "query_products":
            return mock_tool_func
        return None

    ToolRegistry.get_tool_func = MagicMock(side_effect=side_effect_get_tool)

    # Execute
    result = chat_service.ask(mock_db, question="查一下前两个产品")
    
    # Verify
    print("  Result:", result["answer"])
    assert "Test Product 1" in result["answer"]
    print("  ✅ Scenario 1 Passed")

    # --- Scenario 2: Direct Chat ---
    print("\nScenario 2: Direct Chat")
    
    # Reset mock
    mock_client.chat.side_effect = [
        {
            "content": json.dumps({
                "type": "message",
                "content": "你好，我是数据助手。"
            }),
            "trace": {}
        }
    ]
    
    result = chat_service.ask(mock_db, question="你好")
    print("  Result:", result["answer"])
    assert "你好" in result["answer"]
    print("  ✅ Scenario 2 Passed")

    # Cleanup
    chat_service.client = original_client
    ToolRegistry.get_tool_func = original_get_tool
    print("\nAll Tests Passed!")

if __name__ == "__main__":
    test_chat_flow()
