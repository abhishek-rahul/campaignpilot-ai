from __future__ import annotations

from typing import Any

from app.streaming.sse import sse_event


def start_event(*, request_id: str, campaign_id: str | None) -> str:
    return sse_event("start", {"request_id": request_id, "campaign_id": campaign_id})


def token_event(text: str) -> str:
    return sse_event("token", {"text": text})


def brief_delta_event(brief: dict[str, Any]) -> str:
    return sse_event("brief_delta", {"campaign_brief": brief})


def final_event(data: dict[str, Any]) -> str:
    return sse_event("final", data)


def error_event(*, code: str, message: str) -> str:
    return sse_event("error", {"code": code, "message": message})
