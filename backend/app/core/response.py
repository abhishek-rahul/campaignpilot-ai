from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import Request


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_request_id(request: Request | None = None) -> str:
    if request is not None:
        existing = request.headers.get("x-request-id")
        if existing:
            return existing
    return f"req_{uuid4().hex[:12]}"


def success_response(message: str, data: Any = None, request: Request | None = None) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
        "error": None,
        "meta": {
            "request_id": get_request_id(request),
            "timestamp": utc_now_iso(),
        },
    }


def error_response(
    message: str,
    code: str,
    details: list[dict[str, Any]] | None = None,
    request: Request | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": code,
            "details": details or [],
        },
        "meta": {
            "request_id": get_request_id(request),
            "timestamp": utc_now_iso(),
        },
    }


def not_implemented_response(feature: str, request: Request | None = None) -> dict[str, Any]:
    return error_response(
        message=f"{feature} is reserved for its implementation slice",
        code="NOT_IMPLEMENTED_YET",
        details=[{"feature": feature}],
        request=request,
    )
