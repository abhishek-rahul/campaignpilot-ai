from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CampaignBrief, ConversationMessage


def create_message(
    db: Session,
    *,
    message_id: str,
    campaign_id: str,
    sender: str,
    message_text: str,
    message_type: str = "text",
    metadata: dict[str, Any] | None = None,
) -> ConversationMessage:
    message = ConversationMessage(
        id=message_id,
        campaign_id=campaign_id,
        sender=sender,
        message_text=message_text,
        message_type=message_type,
        message_metadata=metadata or {},
    )
    db.add(message)
    db.flush()
    db.refresh(message)
    return message


def list_messages(db: Session, campaign_id: str) -> list[ConversationMessage]:
    return list(
        db.scalars(
            select(ConversationMessage)
            .where(ConversationMessage.campaign_id == campaign_id)
            .order_by(ConversationMessage.created_at.asc(), ConversationMessage.id.asc())
        ).all()
    )


def upsert_brief(
    db: Session,
    *,
    brief_id: str,
    campaign_id: str,
    goal: str | None,
    target_audience: str | None,
    offer_details: str | None,
    tone: str | None,
    preferred_channels: list[str],
    cta_link: str | None,
    expiry_date: date | None,
    missing_fields: list[str],
    brief_status: str,
    raw_user_input: str | None,
    structured_json: dict[str, Any],
) -> CampaignBrief:
    brief = db.scalar(select(CampaignBrief).where(CampaignBrief.campaign_id == campaign_id))
    if brief is None:
        brief = CampaignBrief(id=brief_id, campaign_id=campaign_id)
        db.add(brief)
    brief.goal = goal
    brief.target_audience = target_audience
    brief.offer_details = offer_details
    brief.tone = tone
    brief.preferred_channels = preferred_channels
    brief.cta_link = cta_link
    brief.expiry_date = expiry_date
    brief.missing_fields = missing_fields
    brief.brief_status = brief_status
    brief.raw_user_input = raw_user_input
    brief.structured_json = structured_json
    db.flush()
    db.refresh(brief)
    return brief


def update_brief_fields(db: Session, brief: CampaignBrief, fields: dict[str, object]) -> list[str]:
    updated: list[str] = []
    for field in (
        "goal",
        "target_audience",
        "offer_details",
        "tone",
        "preferred_channels",
        "cta_link",
        "expiry_date",
    ):
        if field in fields:
            setattr(brief, field, fields[field])
            updated.append(field)
    required = ["goal", "target_audience", "offer_details", "tone", "preferred_channels", "cta_link", "expiry_date"]
    missing = [field for field in required if not getattr(brief, field)]
    brief.missing_fields = missing
    brief.brief_status = "COMPLETE" if not missing else "INCOMPLETE"
    db.flush()
    db.refresh(brief)
    return updated
