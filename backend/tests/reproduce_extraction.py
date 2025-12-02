import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.extraction_service import ExtractionService
from app.services.deepseek_client import DeepseekClient
from app.models.extraction import ExtractionTask, ExtractionItem

class TestExtractionService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_client = MagicMock(spec=DeepseekClient)
        self.service = ExtractionService(self.mock_db, self.mock_client)

    def test_run_extraction_stores_usage(self):
        # Setup
        task_id = "12345678-1234-5678-1234-567812345678"
        mock_task = MagicMock(spec=ExtractionTask)
        mock_task.target_fields = ["color", "size"]
        
        mock_item = MagicMock(spec=ExtractionItem)
        mock_item.original_data = {"title": "Blue Shirt"}
        mock_item.status = "PENDING"
        
        self.mock_db.query.return_value.get.return_value = mock_task
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_item]
        
        # Mock client response with usage
        expected_extracted = {"color": "Blue", "size": "L"}
        expected_usage = {"prompt_tokens": 10, "completion_tokens": 5}
        self.mock_client.extract_features_async = AsyncMock(return_value=(expected_extracted, expected_usage))

        # Run
        asyncio.run(self.service.run_extraction(task_id))

        # Verify
        self.mock_client.extract_features_async.assert_called_once()
        
        # Check if usage was stored
        self.assertEqual(mock_item.extracted_data["_usage"], expected_usage)
        self.assertEqual(mock_item.extracted_data["color"], "Blue")
        self.assertEqual(mock_item.status, "SUCCESS")

    def test_prompt_structure(self):
        # Verify that DeepseekClient constructs the prompt correctly (static system prompt)
        client = DeepseekClient()
        client.api_key = "test_key"
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": '{"test": "val"}'}}],
                "usage": {"total": 10}
            }
            mock_post.return_value = mock_response
            
            asyncio.run(client.extract_features_async("product info", ["field1"]))
            
            # Check arguments passed to post
            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]
            
            messages = payload["messages"]
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]["role"], "system")
            self.assertEqual(messages[1]["role"], "user")
            
            # System prompt should contain instructions
            self.assertIn("你是一个电商产品专家", messages[0]["content"])
            # User prompt should only contain product info
            self.assertEqual(messages[1]["content"], "产品信息: product info")

if __name__ == "__main__":
    unittest.main()
