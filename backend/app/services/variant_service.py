from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import LLMError, ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, variant_repository
from app.db.repositories import compliance_repository
from app.llm import llm_client
from app.llm.llm_client import LLMProviderError
from app.observability import trace_service
from app.rag import rag_pipeline
from app.schemas.variant_schema import (
    GenerateVariantsData,
    GenerateVariantsRequest,
    UpdateVariantRequest,
    VariantData,
    VariantListData,
    VariantUpdateData,
)


def generate_variants(db: Session, campaign_id: str, request: GenerateVariantsRequest) -> GenerateVariantsData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign_id)
    if brief is None:
        raise ValidationError("Campaign brief is required before generating variants")
    if brief.brief_status != "COMPLETE":
        raise ValidationError("Campaign brief is incomplete")

    channels = request.channels or brief.preferred_channels or ["telegram"]
    channels = [channel for channel in channels if channel in {"telegram", "whatsapp_mock"}]
    if not channels:
        raise ValidationError("At least one supported channel is required")

    retrieved_contexts = []
    rag_context_payload: list[dict] = []
    if request.use_rag_context:
        _, retrieved_contexts = rag_pipeline.retrieve_and_save_contexts(
            db,
            campaign_id=campaign_id,
            used_for="VARIANT_GENERATION",
            top_k=5,
        )
        rag_context_payload = rag_pipeline.chunks_to_prompt_context(retrieved_contexts)

    prompt_for_failure = None
    try:
        result = llm_client.generate_message_variants(
            campaign_name=campaign.campaign_name,
            goal=brief.goal,
            target_audience=brief.target_audience,
            offer_details=brief.offer_details,
            tone=brief.tone,
            preferred_channels=channels,
            cta_link=brief.cta_link,
            expiry_date=brief.expiry_date,
            variant_count=request.variant_count,
            rag_context=rag_context_payload,
        )
        prompt_for_failure = result.prompt
    except LLMProviderError as exc:
        trace_service.record_llm_failure(
            db,
            campaign_id=campaign_id,
            operation_name="variant_generation",
            model_name="openai",
            prompt=prompt_for_failure,
            error_message=str(exc),
        )
        db.commit()
        raise LLMError() from exc

    variant_rows = []
    for variant in result.data["variants"][: request.variant_count]:
        variant_rows.append(
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
                "context_refs": [
                    {"context_id": context.context_id, "chunk_id": context.chunk_id, "document_id": context.document_id}
                    for context in retrieved_contexts
                ],
            }
        )
    models = variant_repository.create_variants(db, variant_rows)
    campaign_repository.update_campaign_status(db, campaign, "VARIANTS_GENERATED")
    trace_service.record_llm_success(
        db,
        campaign_id=campaign_id,
        operation_name="variant_generation",
        result=result,
        metadata={"variant_count": len(models), "channels": channels, "use_rag_context": request.use_rag_context},
    )
    db.commit()
    return GenerateVariantsData(
        campaign_id=campaign_id,
        variants=[variant_data(model) for model in models],
        retrieved_contexts=[context.model_dump(mode="json") for context in retrieved_contexts],
    )


def list_variants(db: Session, campaign_id: str) -> VariantListData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    latest_results = compliance_repository.latest_results_for_campaign(db, campaign_id)
    return VariantListData(
        campaign_id=campaign_id,
        variants=[
            variant_data(
                model,
                latest_compliance_status=latest_results[model.id].status if model.id in latest_results else None,
                latest_compliance_result_id=latest_results[model.id].id if model.id in latest_results else None,
            )
            for model in variant_repository.list_variants(db, campaign_id)
        ],
    )


def update_variant(db: Session, variant_id: str, request: UpdateVariantRequest) -> VariantUpdateData:
    variant = variant_repository.get_variant(db, variant_id)
    if variant is None:
        raise ResourceNotFoundError("Variant not found")
    fields = request.model_dump(exclude_unset=True)
    if not fields:
        raise ValidationError("At least one variant field is required")
    updated = variant_repository.update_variant_fields(db, variant, fields)
    db.commit()
    db.refresh(variant)
    return VariantUpdateData(
        variant_id=variant.id,
        updated_fields=updated,
        status=variant.status,
        updated_at=variant.updated_at,
    )


def variant_data(
    model: object,
    *,
    latest_compliance_status: str | None = None,
    latest_compliance_result_id: str | None = None,
) -> VariantData:
    return VariantData(
        variant_id=model.id,
        variant_name=model.variant_name,
        channel=model.channel,
        message_body=model.message_body,
        tone=model.tone,
        reason=model.reason,
        risk_level=model.risk_level,
        status=model.status,
        latest_compliance_status=latest_compliance_status,
        latest_compliance_result_id=latest_compliance_result_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
