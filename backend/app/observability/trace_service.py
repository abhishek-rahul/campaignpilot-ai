from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.ids import new_id
from app.db.repositories import llm_trace_repository
from app.llm.llm_client import LLMResult


def record_llm_success(
    db: Session,
    *,
    campaign_id: str | None,
    operation_name: str,
    result: LLMResult,
    metadata: dict[str, Any] | None = None,
) -> None:
    meta = metadata.copy() if metadata else {}
    meta["used_mock"] = result.used_mock
    llm_trace_repository.create_trace(
        db,
        trace_id=new_id("trace"),
        campaign_id=campaign_id,
        operation_name=operation_name,
        model_name=result.model_name,
        prompt=result.prompt,
        response=result.response_text,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        status="SUCCESS",
        metadata=meta,
    )


def record_llm_failure(
    db: Session,
    *,
    campaign_id: str | None,
    operation_name: str,
    model_name: str,
    prompt: str | None,
    error_message: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    llm_trace_repository.create_trace(
        db,
        trace_id=new_id("trace"),
        campaign_id=campaign_id,
        operation_name=operation_name,
        model_name=model_name,
        prompt=prompt,
        response=None,
        status="FAILED",
        error_message=error_message,
        metadata=metadata or {},
    )
