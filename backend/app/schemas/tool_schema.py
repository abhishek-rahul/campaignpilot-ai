from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ToolCallData(BaseModel):
    tool_call_id: str
    tool_name: str
    status: str
    latency_ms: int | None = None
    created_at: datetime | None = None
