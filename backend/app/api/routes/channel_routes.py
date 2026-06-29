from fastapi import APIRouter, Request

from app.core.response import success_response
from app.services import channel_service

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("")
def list_channels(request: Request):
    data = channel_service.list_channels()
    return success_response("Channels fetched successfully", data.model_dump(mode="json"), request)
