from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import LLMTrace


def create_trace(
    db: Session,
    *,
    trace_id: str,
    campaign_id: str | None,
    operation_name: str,
    model_name: str,
    prompt: str | None,
    response: str | None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    latency_ms: int | None = None,
    cost_estimate: Decimal | None = None,
    status: str = "SUCCESS",
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> LLMTrace:
    trace = LLMTrace(
        id=trace_id,
        campaign_id=campaign_id,
        operation_name=operation_name,
        model_name=model_name,
        prompt=prompt,
        response=response,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_estimate=cost_estimate,
        status=status,
        error_message=error_message,
        trace_metadata=metadata or {},
    )
    db.add(trace)
    db.flush()
    db.refresh(trace)
    return trace


def get_trace(db: Session, trace_id: str) -> LLMTrace | None:
    return db.get(LLMTrace, trace_id)


def list_traces(
    db: Session,
    campaign_id: str,
    *,
    operation_name: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[LLMTrace]:
    stmt = select(LLMTrace).where(LLMTrace.campaign_id == campaign_id)
    if operation_name:
        stmt = stmt.where(LLMTrace.operation_name == operation_name)
    if status:
        stmt = stmt.where(LLMTrace.status == status)
    return list(db.scalars(stmt.order_by(LLMTrace.created_at.desc(), LLMTrace.id.desc()).limit(limit)).all())
