from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import success_response
from app.schemas.chat_schema import CampaignChatRequest
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/campaign")
def campaign_chat_message(payload: CampaignChatRequest, request: Request, db: Session = Depends(get_db)):
    data = chat_service.handle_campaign_chat(db, campaign_id=payload.campaign_id, message=payload.message)
    return success_response("Campaign chat response generated successfully", data.model_dump(mode="json"), request)
