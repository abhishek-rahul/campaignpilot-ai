from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import LLMError, ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, refinement_repository, variant_repository
from app.llm import llm_client
from app.llm.llm_client import LLMProviderError
from app.observability import trace_service
from app.rag import rag_pipeline
from app.schemas.refinement_schema import (
    RefineBriefData,
    RefineBriefRequest,
    RefineVariantData,
    RefineVariantRequest,
    RefinementData,
    RefinementListData,
    RegenerateVariantsData,
    RegenerateVariantsRequest,
)
from app.services.campaign_service import brief_data_from_model
from app.services.variant_service import variant_data


def refine_brief(db: Session, campaign_id: str, request: RefineBriefRequest) -> RefineBriefData:
    feedback = request.feedback.strip()
    if not feedback:
        raise ValidationError("Feedback is required")
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign_id)
    if brief is None:
        raise ValidationError("Campaign brief is required before refinement", code="BRIEF_REQUIRED")

    before = brief_data_from_model(brief)
    before_json = before.model_dump(mode="json")
    rag_context = _rag_context(db, campaign_id, request.use_rag_context)
    prompt_for_failure = None
    try:
        result = llm_client.refine_campaign_brief(
            current_brief=before_json,
            feedback=feedback,
            rag_context=rag_context,
        )
        prompt_for_failure = result.prompt
    except LLMProviderError as exc:
        trace_service.record_llm_failure(
            db,
            campaign_id=campaign_id,
            operation_name="brief_refinement",
            model_name="openai",
            prompt=prompt_for_failure,
            error_message=str(exc),
        )
        db.commit()
        raise LLMError() from exc

    trace_id = trace_service.record_llm_success(
        db,
        campaign_id=campaign_id,
        operation_name="brief_refinement",
        result=result,
        metadata={"apply": request.apply, "use_rag_context": request.use_rag_context},
    )
    after_json = _json_safe(result.data)
    if request.apply:
        _apply_brief_result(brief, after_json, feedback)
        campaign.goal = brief.goal
        campaign.campaign_name = after_json.get("campaign_name") or campaign.campaign_name
        if brief.brief_status == "COMPLETE" and campaign.status in {"DRAFT", "BRIEF_EXTRACTED"}:
            campaign_repository.update_campaign_status(db, campaign, "BRIEF_EXTRACTED")
        _apply_safe_reset(campaign)
    refinement = refinement_repository.create_refinement(
        db,
        {
            "id": new_id("ref"),
            "campaign_id": campaign_id,
            "source_type": "campaign_brief",
            "source_id": brief.id,
            "refinement_type": "brief_refinement",
            "user_feedback": feedback,
            "before_json": before_json,
            "after_json": after_json,
            "status": "APPLIED" if request.apply else "GENERATED",
            "llm_trace_id": trace_id,
        },
    )
    db.commit()
    db.refresh(brief)
    db.refresh(campaign)
    return RefineBriefData(
        campaign_id=campaign_id,
        refinement_id=refinement.id,
        applied=request.apply,
        before_brief=before,
        after_brief=brief_data_from_model(brief) if request.apply else _brief_data_from_json(after_json),
        campaign_status=campaign.status,
        selected_variant_id=campaign.selected_variant_id,
    )


def refine_variant(db: Session, variant_id: str, request: RefineVariantRequest) -> RefineVariantData:
    feedback = request.feedback.strip()
    if not feedback:
        raise ValidationError("Feedback is required")
    source = variant_repository.get_variant(db, variant_id)
    if source is None:
        raise ResourceNotFoundError("Variant not found")
    campaign = campaign_repository.get_campaign(db, source.campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, source.campaign_id)
    if brief is None:
        raise ValidationError("Campaign brief is required before variant refinement", code="BRIEF_REQUIRED")

    brief_json = brief_data_from_model(brief).model_dump(mode="json")
    before_json = variant_data(source).model_dump(mode="json")
    rag_context = _rag_context(db, source.campaign_id, request.use_rag_context)
    prompt_for_failure = None
    try:
        result = llm_client.refine_message_variant(
            current_brief=brief_json,
            source_variant=before_json,
            feedback=feedback,
            rag_context=rag_context,
        )
        prompt_for_failure = result.prompt
    except LLMProviderError as exc:
        trace_service.record_llm_failure(
            db,
            campaign_id=source.campaign_id,
            operation_name="variant_refinement",
            model_name="openai",
            prompt=prompt_for_failure,
            error_message=str(exc),
        )
        db.commit()
        raise LLMError() from exc

    refined_payload = result.data["variant"]
    refined_model = variant_repository.create_variants(
        db,
        [
            {
                "id": new_id("var"),
                "campaign_id": source.campaign_id,
                "variant_name": refined_payload["variant_name"],
                "channel": refined_payload.get("channel") or source.channel,
                "message_body": refined_payload["message_body"],
                "tone": refined_payload.get("tone") or source.tone,
                "reason": refined_payload.get("reason"),
                "risk_level": refined_payload.get("risk_level") or "low",
                "status": "GENERATED",
                "context_refs": source.context_refs or [],
            }
        ],
    )[0]
    trace_id = trace_service.record_llm_success(
        db,
        campaign_id=source.campaign_id,
        operation_name="variant_refinement",
        result=result,
        metadata={"source_variant_id": source.id, "use_rag_context": request.use_rag_context},
    )
    refinement = refinement_repository.create_refinement(
        db,
        {
            "id": new_id("ref"),
            "campaign_id": source.campaign_id,
            "source_type": "message_variant",
            "source_id": source.id,
            "refinement_type": "variant_refinement",
            "user_feedback": feedback,
            "before_json": before_json,
            "after_json": variant_data(refined_model).model_dump(mode="json"),
            "status": "GENERATED",
            "llm_trace_id": trace_id,
        },
    )
    db.commit()
    db.refresh(refined_model)
    return RefineVariantData(
        campaign_id=source.campaign_id,
        source_variant_id=source.id,
        refined_variant=variant_data(refined_model),
        refinement_id=refinement.id,
    )


def regenerate_variants(
    db: Session,
    campaign_id: str,
    request: RegenerateVariantsRequest,
) -> RegenerateVariantsData:
    feedback = request.feedback.strip()
    if not feedback:
        raise ValidationError("Feedback is required")
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign_id)
    if brief is None:
        raise ValidationError("Campaign brief is required before regenerating variants", code="BRIEF_REQUIRED")

    channels = request.channels or brief.preferred_channels or ["telegram"]
    channels = [channel for channel in channels if channel in {"telegram", "whatsapp_mock"}]
    if not channels:
        raise ValidationError("At least one supported channel is required")
    rag_context = _rag_context(db, campaign_id, request.use_rag_context)
    before_json = {"brief": brief_data_from_model(brief).model_dump(mode="json"), "feedback": feedback}
    prompt_for_failure = None
    try:
        result = llm_client.generate_message_variants(
            campaign_name=campaign.campaign_name,
            goal=f"{brief.goal or ''}\nRefinement feedback: {feedback}".strip(),
            target_audience=brief.target_audience,
            offer_details=brief.offer_details,
            tone=brief.tone,
            preferred_channels=channels,
            cta_link=brief.cta_link,
            expiry_date=brief.expiry_date,
            variant_count=request.variant_count,
            rag_context=rag_context,
        )
        prompt_for_failure = result.prompt
    except LLMProviderError as exc:
        trace_service.record_llm_failure(
            db,
            campaign_id=campaign_id,
            operation_name="variant_regeneration",
            model_name="openai",
            prompt=prompt_for_failure,
            error_message=str(exc),
        )
        db.commit()
        raise LLMError() from exc

    variant_rows = [
        {
            "id": new_id("var"),
            "campaign_id": campaign_id,
            "variant_name": variant["variant_name"],
            "channel": variant["channel"],
            "message_body": variant["message_body"],
            "tone": variant.get("tone"),
            "reason": variant.get("reason"),
            "risk_level": variant.get("risk_level") or "low",
            "status": "GENERATED",
            "context_refs": [],
        }
        for variant in result.data["variants"][: request.variant_count]
    ]
    models = variant_repository.create_variants(db, variant_rows)
    trace_id = trace_service.record_llm_success(
        db,
        campaign_id=campaign_id,
        operation_name="variant_regeneration",
        result=result,
        metadata={"variant_count": len(models), "channels": channels, "use_rag_context": request.use_rag_context},
    )
    refinement = refinement_repository.create_refinement(
        db,
        {
            "id": new_id("ref"),
            "campaign_id": campaign_id,
            "source_type": "campaign_brief",
            "source_id": brief.id,
            "refinement_type": "variant_regeneration",
            "user_feedback": feedback,
            "before_json": before_json,
            "after_json": {"variants": [variant_data(model).model_dump(mode="json") for model in models]},
            "status": "GENERATED",
            "llm_trace_id": trace_id,
        },
    )
    db.commit()
    return RegenerateVariantsData(
        campaign_id=campaign_id,
        refinement_id=refinement.id,
        variants=[variant_data(model) for model in models],
    )


def list_refinements(
    db: Session,
    campaign_id: str,
    *,
    refinement_type: str | None = None,
    source_type: str | None = None,
) -> RefinementListData:
    if campaign_repository.get_campaign(db, campaign_id) is None:
        raise ResourceNotFoundError("Campaign not found")
    rows = refinement_repository.list_refinements(
        db,
        campaign_id,
        refinement_type=refinement_type,
        source_type=source_type,
    )
    return RefinementListData(campaign_id=campaign_id, refinements=[_refinement_data(row) for row in rows])


def _rag_context(db: Session, campaign_id: str, use_rag_context: bool) -> list[dict[str, Any]]:
    if not use_rag_context:
        return []
    contexts = rag_pipeline.list_saved_contexts(db, campaign_id=campaign_id)
    return rag_pipeline.chunks_to_prompt_context(contexts)


def _apply_brief_result(brief: Any, data: dict[str, Any], feedback: str) -> None:
    brief.goal = data.get("goal")
    brief.target_audience = data.get("target_audience")
    brief.offer_details = data.get("offer_details")
    brief.tone = data.get("tone")
    brief.preferred_channels = data.get("preferred_channels") or []
    brief.cta_link = data.get("cta_link")
    brief.expiry_date = data.get("expiry_date")
    brief.missing_fields = data.get("missing_fields") or []
    brief.brief_status = data.get("brief_status") or ("COMPLETE" if not brief.missing_fields else "INCOMPLETE")
    brief.raw_user_input = feedback
    brief.structured_json = {key: _json_safe(value) for key, value in data.items()}


def _apply_safe_reset(campaign: Any) -> None:
    if campaign.selected_variant_id or campaign.status in {"APPROVED", "PAYLOADS_GENERATED", "SENT"}:
        campaign.status = "NEEDS_REVIEW"
        campaign.selected_variant_id = None


def _brief_data_from_json(data: dict[str, Any]):
    from app.schemas.campaign_schema import CampaignBriefData

    return CampaignBriefData(
        goal=data.get("goal"),
        target_audience=data.get("target_audience"),
        offer_details=data.get("offer_details"),
        tone=data.get("tone"),
        preferred_channels=data.get("preferred_channels") or [],
        cta_link=data.get("cta_link"),
        expiry_date=data.get("expiry_date"),
        missing_fields=data.get("missing_fields") or [],
        brief_status=data.get("brief_status") or "INCOMPLETE",
    )


def _refinement_data(row: Any) -> RefinementData:
    return RefinementData(
        refinement_id=row.id,
        campaign_id=row.campaign_id,
        source_type=row.source_type,
        source_id=row.source_id,
        refinement_type=row.refinement_type,
        user_feedback=row.user_feedback,
        before_json=row.before_json or {},
        after_json=row.after_json or {},
        status=row.status,
        llm_trace_id=row.llm_trace_id,
        created_at=row.created_at,
    )


def _json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[no-any-return]
    return value
