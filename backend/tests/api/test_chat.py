from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class FakeChatService:
    def ask(self, *_, **__):  # type: ignore[override]
        return {
            "answer": "测试回答",
            "references": [],
            "session_id": "fake",
        }


def test_chat_query(monkeypatch):
    from app.services import chat_service as service_module

    monkeypatch.setattr(service_module, "chat_service", FakeChatService())

    response = client.post("/api/chat/query", json={"question": "最近的批次情况?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "测试回答"
    assert data["sessionId"] == "fake"
    assert isinstance(data.get("references"), list)
