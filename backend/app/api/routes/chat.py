from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
# 注意：为便于单测通过 monkeypatch 替换 chat_service，这里导入模块而非对象
from app.services import chat_service as service_module


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question: str = Field(..., min_length=2)
    context_batches: list[str] | None = Field(default=None, alias="contextBatches")


class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    answer: str
    references: list[dict] | None = None
    session_id: str = Field(..., alias="sessionId")


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    # 通过模块属性访问，方便测试用例 monkeypatch: service_module.chat_service = FakeChatService()
    result = service_module.chat_service.ask(
        db,
        question=payload.question,
        context_batches=payload.context_batches,
    )
    return ChatResponse(**result)
