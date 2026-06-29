from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.db.models import (
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
from app.db.repositories import (
    campaign_repository,
    llm_trace_repository,
    observability_repository,
    tool_call_repository,
)
from app.schemas.observability_schema import (
    DebugTimelineData,
    DebugTimelineEventData,
    LLMTraceDetailData,
    LLMTraceListData,
    LLMTracePreviewData,
    ObservabilitySummaryData,
    ToolCallDetailData,
    ToolCallListData,
    ToolCallPreviewData,
)

PREVIEW_LIMIT = 180


def get_campaign_summary(db: Session, campaign_id: str) -> ObservabilitySummaryData:
    _ensure_campaign(db, campaign_id)
    llm_count, latest_llm = observability_repository.count_and_latest(db, LLMTrace, campaign_id)
    context_count, _ = observability_repository.count_and_latest(db, RetrievedContext, campaign_id)
    compliance_count, _ = observability_repository.count_and_latest(db, ComplianceResult, campaign_id)
    tool_count, latest_tool = observability_repository.count_and_latest(db, ToolCallLog, campaign_id)
    payload_count, _ = observability_repository.count_and_latest(db, ChannelPayload, campaign_id)
    delivery_count, latest_delivery = observability_repository.count_and_latest(db, DeliveryLog, campaign_id)
    refinement_count, latest_refinement = observability_repository.count_and_latest(db, CampaignRefinement, campaign_id)
    evaluation_count, latest_evaluation = observability_repository.count_and_latest(db, EvaluationResult, campaign_id)
    return ObservabilitySummaryData(
        campaign_id=campaign_id,
        llm_trace_count=llm_count,
        retrieved_context_count=context_count,
        compliance_result_count=compliance_count,
        tool_call_count=tool_count,
        payload_count=payload_count,
        delivery_log_count=delivery_count,
        refinement_count=refinement_count,
        evaluation_count=evaluation_count,
        latest_llm_trace_at=latest_llm,
        latest_tool_call_at=latest_tool,
        latest_delivery_at=latest_delivery,
        latest_refinement_at=latest_refinement,
        latest_evaluation_at=latest_evaluation,
    )


def list_campaign_llm_traces(
    db: Session,
    campaign_id: str,
    *,
    operation_name: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> LLMTraceListData:
    _ensure_campaign(db, campaign_id)
    traces = llm_trace_repository.list_traces(
        db,
        campaign_id,
        operation_name=operation_name,
        status=status,
        limit=min(max(limit, 1), 100),
    )
    return LLMTraceListData(campaign_id=campaign_id, traces=[_trace_preview(trace) for trace in traces])


def get_llm_trace_detail(db: Session, trace_id: str) -> LLMTraceDetailData:
    trace = llm_trace_repository.get_trace(db, trace_id)
    if trace is None:
        raise ResourceNotFoundError("LLM trace not found")
    return LLMTraceDetailData(
        trace_id=trace.id,
        campaign_id=trace.campaign_id,
        operation_name=trace.operation_name,
        model_name=trace.model_name,
        used_mock=bool((trace.trace_metadata or {}).get("used_mock")),
        prompt=trace.prompt,
        response_text=trace.response,
        input_tokens=trace.input_tokens,
        output_tokens=trace.output_tokens,
        latency_ms=trace.latency_ms,
        status=trace.status,
        error_message=trace.error_message,
        metadata=trace.trace_metadata or {},
        created_at=trace.created_at,
    )


def list_campaign_tool_calls(
    db: Session,
    campaign_id: str,
    *,
    tool_name: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> ToolCallListData:
    _ensure_campaign(db, campaign_id)
    logs = tool_call_repository.list_tool_call_logs(
        db,
        campaign_id,
        tool_name=tool_name,
        status=status,
        limit=min(max(limit, 1), 100),
    )
    return ToolCallListData(campaign_id=campaign_id, tool_calls=[_tool_preview(log) for log in logs])


def get_tool_call_detail(db: Session, tool_call_id: str) -> ToolCallDetailData:
    log = tool_call_repository.get_tool_call_log(db, tool_call_id)
    if log is None:
        raise ResourceNotFoundError("Tool call log not found")
    return ToolCallDetailData(
        tool_call_id=log.id,
        campaign_id=log.campaign_id,
        variant_id=log.variant_id,
        tool_name=log.tool_name,
        input_json=log.input_json or {},
        output_json=log.output_json or {},
        status=log.status,
        latency_ms=log.latency_ms,
        error_message=log.error_message,
        created_at=log.created_at,
    )


def get_debug_timeline(db: Session, campaign_id: str) -> DebugTimelineData:
    _ensure_campaign(db, campaign_id)
    rows_by_type = observability_repository.timeline_rows(db, campaign_id)
    events: list[DebugTimelineEventData] = []
    for event_type, rows in rows_by_type.items():
        events.extend(_timeline_event(event_type, row) for row in rows)
    events.sort(key=lambda event: (event.created_at, event.event_id))
    return DebugTimelineData(campaign_id=campaign_id, events=events[:100])


def _ensure_campaign(db: Session, campaign_id: str) -> None:
    if campaign_repository.get_campaign(db, campaign_id) is None:
        raise ResourceNotFoundError("Campaign not found")


def _trace_preview(trace: Any) -> LLMTracePreviewData:
    return LLMTracePreviewData(
        trace_id=trace.id,
        operation_name=trace.operation_name,
        model_name=trace.model_name,
        used_mock=bool((trace.trace_metadata or {}).get("used_mock")),
        latency_ms=trace.latency_ms,
        status=trace.status,
        prompt_preview=_preview(trace.prompt),
        response_preview=_preview(trace.response),
        error_message=trace.error_message,
        created_at=trace.created_at,
    )


def _tool_preview(log: Any) -> ToolCallPreviewData:
    return ToolCallPreviewData(
        tool_call_id=log.id,
        tool_name=log.tool_name,
        status=log.status,
        latency_ms=log.latency_ms,
        error_message=log.error_message,
        created_at=log.created_at,
    )


def _timeline_event(event_type: str, row: Any) -> DebugTimelineEventData:
    title, summary = _timeline_text(event_type, row)
    return DebugTimelineEventData(
        event_id=f"{event_type}_{row.id}",
        event_type=event_type,
        title=title,
        summary=summary,
        created_at=row.created_at,
        related_id=row.id,
    )


def _timeline_text(event_type: str, row: Any) -> tuple[str, str]:
    if isinstance(row, ConversationMessage):
        return f"{row.sender} message", _preview(row.message_text) or ""
    if isinstance(row, LLMTrace):
        return f"LLM {row.operation_name}", f"{row.status} via {row.model_name}"
    if isinstance(row, RetrievedContext):
        return f"RAG context {row.used_for}", _preview(row.retrieved_text) or ""
    if isinstance(row, ComplianceResult):
        return "Compliance result", f"{row.status} / {row.risk_level}"
    if isinstance(row, ToolCallLog):
        return f"Tool call {row.tool_name}", row.status
    if isinstance(row, ChannelPayload):
        return f"Payload {row.channel}", row.status
    if isinstance(row, DeliveryLog):
        return f"Delivery {row.channel}", row.status
    if isinstance(row, CampaignRefinement):
        return f"Refinement {row.refinement_type}", _preview(row.user_feedback) or ""
    if isinstance(row, EvaluationResult):
        return f"Evaluation {row.evaluation_type}", f"{row.grade} ({row.score})"
    return event_type, row.id


def _preview(value: str | None, limit: int = PREVIEW_LIMIT) -> str | None:
    if value is None:
        return None
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 3]}..."
