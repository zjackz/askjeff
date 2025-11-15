from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.chat_service import chat_service


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2)
    contextBatches: list[str] | None = Field(default=None, alias="context_batches")


class ChatResponse(BaseModel):
    answer: str
    references: dict | None
    session_id: str


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    result = chat_service.ask(
        db,
        question=payload.question,
        context_batches=payload.contextBatches,
    )
    return ChatResponse(**result)
