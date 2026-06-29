from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ObservabilitySummaryData(BaseModel):
    campaign_id: str
    llm_trace_count: int = 0
    retrieved_context_count: int = 0
    compliance_result_count: int = 0
    tool_call_count: int = 0
    payload_count: int = 0
    delivery_log_count: int = 0
    refinement_count: int = 0
    evaluation_count: int = 0
    latest_llm_trace_at: datetime | None = None
    latest_tool_call_at: datetime | None = None
    latest_delivery_at: datetime | None = None
    latest_refinement_at: datetime | None = None
    latest_evaluation_at: datetime | None = None


class LLMTracePreviewData(BaseModel):
    trace_id: str
    operation_name: str
    model_name: str
    used_mock: bool = False
    latency_ms: int | None = None
    status: str
    prompt_preview: str | None = None
    response_preview: str | None = None
    error_message: str | None = None
    created_at: datetime


class LLMTraceListData(BaseModel):
    campaign_id: str
    traces: list[LLMTracePreviewData] = Field(default_factory=list)


class LLMTraceDetailData(BaseModel):
    trace_id: str
    campaign_id: str | None = None
    operation_name: str
    model_name: str
    used_mock: bool = False
    prompt: str | None = None
    response_text: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int | None = None
    status: str
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ToolCallPreviewData(BaseModel):
    tool_call_id: str
    tool_name: str
    status: str
    latency_ms: int | None = None
    error_message: str | None = None
    created_at: datetime


class ToolCallListData(BaseModel):
    campaign_id: str
    tool_calls: list[ToolCallPreviewData] = Field(default_factory=list)


class ToolCallDetailData(BaseModel):
    tool_call_id: str
    campaign_id: str | None = None
    variant_id: str | None = None
    tool_name: str
    input_json: dict[str, Any] = Field(default_factory=dict)
    output_json: dict[str, Any] = Field(default_factory=dict)
    status: str
    latency_ms: int | None = None
    error_message: str | None = None
    created_at: datetime


class DebugTimelineEventData(BaseModel):
    event_id: str
    event_type: str
    title: str
    summary: str
    created_at: datetime
    related_id: str | None = None


class DebugTimelineData(BaseModel):
    campaign_id: str
    events: list[DebugTimelineEventData] = Field(default_factory=list)
