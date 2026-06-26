from fastapi import APIRouter, Request

from app.core.response import not_implemented_response

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("")
def list_channels(request: Request):
    return not_implemented_response("Slice 4 - List Channels", request)
