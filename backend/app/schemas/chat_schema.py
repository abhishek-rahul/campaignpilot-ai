from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.campaign_schema import CampaignBriefData


class CampaignChatRequest(BaseModel):
    campaign_id: str | None = None
    message: str = Field(min_length=1)
    stream: bool = False


class CampaignChatData(BaseModel):
    campaign_id: str
    conversation_message_id: str
    ai_message_id: str
    ai_reply: str
    brief_status: str
    missing_fields: list[str]
    campaign_brief: CampaignBriefData


class ConversationMessageData(BaseModel):
    message_id: str
    sender: str
    message_text: str
    message_type: str
    created_at: datetime


class ConversationData(BaseModel):
    campaign_id: str
    messages: list[ConversationMessageData]
