from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ImportBatch, ProductRecord, QuerySession
from app.services.audit_service import AuditService
from app.services.deepseek_client import DeepseekClient


class ChatService:
    def __init__(self, client: DeepseekClient | None = None) -> None:
        self.client = client or DeepseekClient()

    def ask(
        self,
        db: Session,
        *,
        question: str,
        context_batches: list[str] | None = None,
        asked_by: str | None = None,
    ) -> dict[str, Any]:
        summary = self._collect_summary(db, context_batches)
        result = self.client.summarize(question, summary)

        session = QuerySession(
            question=question,
            intent="batch-analysis",
            sql_template=summary.get("sql"),
            answer=result["answer"],
            references={"batches": summary.get("batch_ids", [])},
            deepseek_trace=result.get("trace"),
            status="succeeded",
            asked_by=asked_by,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        AuditService.log_action(
            db,
            action="chat.ask",
            actor_id=asked_by,
            entity_id=session.id,
            payload={"question": question, "references": session.references},
        )

        return {
            "answer": session.answer,
            "references": session.references,
            "session_id": session.id,
        }

    def _collect_summary(self, db: Session, batch_ids: list[str] | None) -> dict[str, Any]:
        stmt = select(func.count(ImportBatch.id))
        if batch_ids:
            stmt = stmt.where(ImportBatch.id.in_(batch_ids))
        batch_count = db.scalar(stmt) or 0

        product_stmt = select(func.count(ProductRecord.id))
        if batch_ids:
            product_stmt = product_stmt.where(ProductRecord.batch_id.in_(batch_ids))
        product_count = db.scalar(product_stmt) or 0

        latest_stmt = (
            select(ImportBatch.id, ImportBatch.success_rows)
            .order_by(ImportBatch.finished_at.desc().nullslast())
            .limit(1)
        )
        latest_batch = db.execute(latest_stmt).one_or_none()

        summary = {
            "batch_summary": {
                "batch_count": batch_count,
                "product_count": product_count,
                "latest_batch_id": latest_batch[0] if latest_batch else None,
                "latest_rows": latest_batch[1] if latest_batch else 0,
            },
            "batch_ids": batch_ids or [],
            "sql": "SELECT COUNT(*) FROM import_batches",
        }
        return summary


chat_service = ChatService()
