import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Mock dependencies before import
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["app.models"] = MagicMock()
sys.modules["app.services.audit_service"] = MagicMock()
sys.modules["app.services.log_service"] = MagicMock()
sys.modules["httpx"] = MagicMock()

# Mock QuerySession to act like a real object
class RealQuerySession:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = "mock_id"

sys.modules["app.models"].QuerySession = RealQuerySession

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.services.tool_registry import ToolRegistry
from app.services.chat_service import ChatService
from app.services.deepseek_client import DeepseekClient

def test_tool_registry():
    print("Testing ToolRegistry...")
    
    def dummy_tool(db, param1):
        return f"Result: {param1}"
    
    schema = {
        "type": "object",
        "properties": {
            "param1": {"type": "string"}
        }
    }
    
    ToolRegistry.register("dummy_tool", dummy_tool, schema)
    
    tool = ToolRegistry.get_tool("dummy_tool")
    assert tool is not None
    assert tool(None, param1="test") == "Result: test"
    
    schemas = ToolRegistry.get_schemas()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "dummy_tool"
    print("ToolRegistry OK")

def test_deepseek_client_mock():
    print("Testing DeepseekClient (Mock)...")
    
    class MockClient(DeepseekClient):
        def __init__(self):
            self.call_count = 0
            
        def chat(self, messages, json_mode=False, temperature=0.1, system_prompt=None):
            self.call_count += 1
            print(f"Mock Chat Call #{self.call_count}")
            if self.call_count == 1:
                # First call: Intent recognition
                return {
                    "content": '{"type": "tool_call", "tool": "dummy_tool", "params": {"param1": "value"}}',
                    "trace": {}
                }
            else:
                # Second call: Answer generation
                return {
                    "content": "Final Answer: Executed with value",
                    "trace": {}
                }
            
    client = MockClient()
    service = ChatService(client)
    
    # Register dummy tool
    def dummy_tool(db, param1):
        return f"Executed with {param1}"
    
    ToolRegistry.register("dummy_tool", dummy_tool, {})
    
    # Mock DB session
    class MockSession:
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass
    
    # Test ask
    result = service.ask(MockSession(), question="Test question")
    print(f"Result: {result}")
    assert "Executed with value" in result["answer"]
    print("ChatService Flow OK")

if __name__ == "__main__":
    test_tool_registry()
    test_deepseek_client_mock()
