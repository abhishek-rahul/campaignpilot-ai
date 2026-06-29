from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import get_request_id, success_response
from app.schemas.chat_schema import CampaignChatRequest
from app.services import chat_service, streaming_chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/campaign/stream")
def campaign_chat_message_stream(payload: CampaignChatRequest, request: Request, db: Session = Depends(get_db)):
    request_id = get_request_id(request)
    return StreamingResponse(
        streaming_chat_service.stream_campaign_chat(db, payload, request_id=request_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Request-ID": request_id},
    )


@router.post("/campaign")
def campaign_chat_message(payload: CampaignChatRequest, request: Request, db: Session = Depends(get_db)):
    data = chat_service.handle_campaign_chat(db, campaign_id=payload.campaign_id, message=payload.message)
    return success_response("Campaign chat response generated successfully", data.model_dump(mode="json"), request)
