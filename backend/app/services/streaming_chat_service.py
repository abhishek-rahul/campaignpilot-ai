from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.core.exceptions import CampaignPilotError, ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, chat_repository
from app.llm import llm_client
from app.llm.llm_client import LLMProviderError
from app.llm.streaming import chunk_text
from app.observability import trace_service
from app.schemas.chat_schema import CampaignChatRequest
from app.services.campaign_service import brief_data_from_model
from app.streaming import event_builder


def stream_campaign_chat(db: Session, payload: CampaignChatRequest, *, request_id: str) -> Iterator[str]:
    yield event_builder.start_event(request_id=request_id, campaign_id=payload.campaign_id)
    try:
        data = _handle_streaming_chat(db, payload)
        for token in chunk_text(data["ai_reply"]):
            yield event_builder.token_event(token)
        yield event_builder.brief_delta_event(data["campaign_brief"])
        yield event_builder.final_event(data)
    except CampaignPilotError as exc:
        db.rollback()
        yield event_builder.error_event(code=exc.code, message=exc.message)
    except LLMProviderError:
        db.rollback()
        yield event_builder.error_event(code="LLM_PROVIDER_ERROR", message="LLM provider failed")
    except Exception:  # noqa: BLE001
        db.rollback()
        yield event_builder.error_event(code="INTERNAL_SERVER_ERROR", message="Unexpected backend error")


def _handle_streaming_chat(db: Session, payload: CampaignChatRequest) -> dict:
    message = payload.message.strip()
    if not message:
        raise ValidationError("Chat message is required")
    campaign = campaign_repository.get_campaign(db, payload.campaign_id) if payload.campaign_id else None
    if payload.campaign_id and campaign is None:
        raise ResourceNotFoundError("Campaign not found")

    prompt_for_failure = None
    try:
        result = llm_client.extract_campaign_brief(message)
        prompt_for_failure = result.prompt
    except LLMProviderError as exc:
        trace_service.record_llm_failure(
            db,
            campaign_id=payload.campaign_id,
            operation_name="streaming_brief_extraction",
            model_name="openai",
            prompt=prompt_for_failure,
            error_message=str(exc),
        )
        db.commit()
        raise

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
        message_text=message,
        metadata={"streaming": True},
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
        metadata={"brief_status": brief.brief_status, "missing_fields": brief.missing_fields, "streaming": True},
    )
    trace_id = trace_service.record_llm_success(
        db,
        campaign_id=campaign.id,
        operation_name="streaming_brief_extraction",
        result=result,
    )
    db.commit()
    db.refresh(brief)
    return {
        "campaign_id": campaign.id,
        "conversation_message_id": user_message.id,
        "ai_message_id": ai_message.id,
        "ai_reply": ai_reply,
        "brief_status": brief.brief_status,
        "missing_fields": brief.missing_fields,
        "campaign_brief": brief_data_from_model(brief).model_dump(mode="json"),
        "llm_trace_id": trace_id,
    }


def _json_safe(value: object) -> object:
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[no-any-return]
    return value
