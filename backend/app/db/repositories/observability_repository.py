from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    Approval,
    CampaignRefinement,
    ChannelPayload,
    ComplianceResult,
    ConversationMessage,
    DeliveryLog,
    EvaluationResult,
    LLMTrace,
    RetrievedContext,
    ToolCallLog,
)


def count_and_latest(db: Session, model: Any, campaign_id: str) -> tuple[int, object | None]:
    count = db.scalar(select(func.count()).select_from(model).where(model.campaign_id == campaign_id)) or 0
    latest = db.scalar(select(func.max(model.created_at)).where(model.campaign_id == campaign_id))
    return count, latest


def timeline_rows(db: Session, campaign_id: str, *, limit_per_type: int = 50) -> dict[str, list[Any]]:
    return {
        "conversation_message": _rows(db, ConversationMessage, campaign_id, limit_per_type),
        "llm_trace": _rows(db, LLMTrace, campaign_id, limit_per_type),
        "retrieved_context": _rows(db, RetrievedContext, campaign_id, limit_per_type),
        "compliance_result": _rows(db, ComplianceResult, campaign_id, limit_per_type),
        "tool_call": _rows(db, ToolCallLog, campaign_id, limit_per_type),
        "approval": _rows(db, Approval, campaign_id, limit_per_type),
        "channel_payload": _rows(db, ChannelPayload, campaign_id, limit_per_type),
        "delivery_log": _rows(db, DeliveryLog, campaign_id, limit_per_type),
        "campaign_refinement": _rows(db, CampaignRefinement, campaign_id, limit_per_type),
        "evaluation_result": _rows(db, EvaluationResult, campaign_id, limit_per_type),
    }


def _rows(db: Session, model: Any, campaign_id: str, limit: int) -> list[Any]:
    return list(
        db.scalars(
            select(model)
            .where(model.campaign_id == campaign_id)
            .order_by(model.created_at.asc(), model.id.asc())
            .limit(limit)
        ).all()
    )
