from fastapi import APIRouter, Request

from app.core.response import success_response

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check(request: Request):
    return success_response(
        "Health check successful",
        {"status": "ok", "service": "campaignpilot-api", "version": "0.1.0"},
        request,
    )
