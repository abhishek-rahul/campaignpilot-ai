from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LLMTraceData(BaseModel):
    trace_id: str
    campaign_id: str | None = None
    operation_name: str
    model_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int | None = None
    status: str
    created_at: datetime
