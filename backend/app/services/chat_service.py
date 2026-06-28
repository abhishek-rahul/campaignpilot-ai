from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import LLMError, ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, chat_repository
from app.llm import llm_client
from app.llm.llm_client import LLMProviderError
from app.observability import trace_service
from app.schemas.chat_schema import CampaignChatData, ConversationData, ConversationMessageData
from app.services.campaign_service import brief_data_from_model


def handle_campaign_chat(db: Session, *, campaign_id: str | None, message: str) -> CampaignChatData:
    if not message.strip():
        raise ValidationError("Chat message is required")
    campaign = campaign_repository.get_campaign(db, campaign_id) if campaign_id else None
    if campaign_id and campaign is None:
        raise ResourceNotFoundError("Campaign not found")

    prompt_for_failure: str | None = None
    try:
        result = llm_client.extract_campaign_brief(message)
        prompt_for_failure = result.prompt
    except LLMProviderError as exc:
        trace_service.record_llm_failure(
            db,
            campaign_id=campaign_id,
            operation_name="brief_extraction",
            model_name="openai",
            prompt=prompt_for_failure,
            error_message=str(exc),
        )
        db.commit()
        raise LLMError() from exc

    if campaign is None:
        campaign = campaign_repository.create_campaign(
            db,
            campaign_id=new_id("camp"),
            campaign_name=result.data.get("campaign_name") or "CampaignPilot Draft Campaign",
            goal=result.data.get("goal"),
        )

    user_message = chat_repository.create_message(
        db,
        message_id=new_id("msg"),
        campaign_id=campaign.id,
        sender="CAMPAIGN_MANAGER",
        message_text=message.strip(),
    )
    brief = chat_repository.upsert_brief(
        db,
        brief_id=new_id("brief"),
        campaign_id=campaign.id,
        goal=result.data.get("goal"),
        target_audience=result.data.get("target_audience"),
        offer_details=result.data.get("offer_details"),
        tone=result.data.get("tone"),
        preferred_channels=result.data.get("preferred_channels") or [],
        cta_link=result.data.get("cta_link"),
        expiry_date=result.data.get("expiry_date"),
        missing_fields=result.data.get("missing_fields") or [],
        brief_status=result.data.get("brief_status") or "INCOMPLETE",
        raw_user_input=message,
        structured_json={key: _json_safe(value) for key, value in result.data.items()},
    )
    campaign.campaign_name = result.data.get("campaign_name") or campaign.campaign_name
    campaign.goal = brief.goal
    if brief.brief_status == "COMPLETE":
        campaign_repository.update_campaign_status(db, campaign, "BRIEF_EXTRACTED")

    ai_reply = result.data.get("ai_reply") or "I captured your campaign brief."
    ai_message = chat_repository.create_message(
        db,
        message_id=new_id("msg"),
        campaign_id=campaign.id,
        sender="AI_AGENT",
        message_text=ai_reply,
        metadata={"brief_status": brief.brief_status, "missing_fields": brief.missing_fields},
    )
    trace_service.record_llm_success(
        db,
        campaign_id=campaign.id,
        operation_name="brief_extraction",
        result=result,
    )
    db.commit()
    db.refresh(brief)
    return CampaignChatData(
        campaign_id=campaign.id,
        conversation_message_id=user_message.id,
        ai_message_id=ai_message.id,
        ai_reply=ai_reply,
        brief_status=brief.brief_status,
        missing_fields=brief.missing_fields,
        campaign_brief=brief_data_from_model(brief),
    )


def get_conversation(db: Session, campaign_id: str) -> ConversationData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    messages = chat_repository.list_messages(db, campaign_id)
    return ConversationData(
        campaign_id=campaign_id,
        messages=[
            ConversationMessageData(
                message_id=message.id,
                sender=message.sender,
                message_text=message.message_text,
                message_type=message.message_type,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )


def _json_safe(value: object) -> object:
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[no-any-return]
    return value
