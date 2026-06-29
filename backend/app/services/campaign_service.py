from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import approval_repository, campaign_repository, chat_repository, compliance_repository, variant_repository
from app.llm import llm_client
from app.observability import trace_service
from app.rag import rag_pipeline
from app.schemas.campaign_schema import (
    CampaignBriefData,
    CampaignCreateData,
    CampaignDetailData,
    CampaignListData,
    CampaignListItem,
    CampaignUpdateData,
    CreateCampaignRequest,
    UpdateCampaignRequest,
)
from app.schemas.common_schema import Pagination
from app.schemas.rag_schema import CampaignPlanData, RetrievedContextListData
from app.schemas.compliance_schema import CampaignComplianceSummaryData, VariantComplianceSummaryItem


def create_campaign(db: Session, request: CreateCampaignRequest) -> CampaignCreateData:
    if not request.campaign_name.strip():
        raise ValidationError("Campaign name is required")
    campaign = campaign_repository.create_campaign(
        db,
        campaign_id=new_id("camp"),
        campaign_name=request.campaign_name.strip(),
        goal=request.goal,
        status="DRAFT",
    )
    missing = _missing_fields(request.model_dump())
    chat_repository.upsert_brief(
        db,
        brief_id=new_id("brief"),
        campaign_id=campaign.id,
        goal=request.goal,
        target_audience=request.target_audience,
        offer_details=request.offer_details,
        tone=request.tone,
        preferred_channels=request.preferred_channels,
        cta_link=request.cta_link,
        expiry_date=request.expiry_date,
        missing_fields=missing,
        brief_status="COMPLETE" if not missing else "INCOMPLETE",
        raw_user_input=None,
        structured_json=request.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(campaign)
    return CampaignCreateData(
        campaign_id=campaign.id,
        campaign_name=campaign.campaign_name,
        status=campaign.status,
        created_at=campaign.created_at,
    )


def list_campaigns(db: Session, *, page: int = 1, page_size: int = 20, status: str | None = None) -> CampaignListData:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    campaigns, total = campaign_repository.list_campaigns(db, page=page, page_size=page_size, status=status)
    return CampaignListData(
        items=[
            CampaignListItem(
                campaign_id=campaign.id,
                campaign_name=campaign.campaign_name,
                status=campaign.status,
                created_at=campaign.created_at,
            )
            for campaign in campaigns
        ],
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=campaign_repository.count_total_pages(total, page_size),
        ),
    )


def get_campaign_detail(db: Session, campaign_id: str) -> CampaignDetailData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    return _campaign_detail(campaign)


def update_campaign(db: Session, campaign_id: str, request: UpdateCampaignRequest) -> CampaignUpdateData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    fields = request.model_dump(exclude_unset=True)
    if not fields:
        raise ValidationError("At least one campaign field is required")

    campaign_updates = campaign_repository.update_campaign_fields(db, campaign, fields)
    brief = campaign_repository.get_brief_for_campaign(db, campaign.id)
    brief_updates: list[str] = []
    if brief is not None:
        brief_updates = chat_repository.update_brief_fields(db, brief, fields)
        if brief.brief_status == "COMPLETE" and campaign.status == "DRAFT":
            campaign_repository.update_campaign_status(db, campaign, "BRIEF_EXTRACTED")
    db.commit()
    db.refresh(campaign)
    return CampaignUpdateData(
        campaign_id=campaign.id,
        updated_fields=campaign_repository.normalize_updated_fields(campaign_updates, brief_updates),
        status=campaign.status,
        updated_at=campaign.updated_at,
    )


def get_retrieved_context(db: Session, campaign_id: str, *, refresh: bool = False, top_k: int = 5) -> RetrievedContextListData:
    if campaign_repository.get_campaign(db, campaign_id) is None:
        raise ResourceNotFoundError("Campaign not found")
    contexts = rag_pipeline.list_saved_contexts(db, campaign_id=campaign_id)
    if refresh or not contexts:
        _, contexts = rag_pipeline.retrieve_and_save_contexts(
            db,
            campaign_id=campaign_id,
            used_for="CONTEXT_PREVIEW",
            top_k=top_k,
        )
        db.commit()
    return RetrievedContextListData(campaign_id=campaign_id, contexts=contexts)


def generate_campaign_plan(db: Session, campaign_id: str, *, top_k: int = 5) -> CampaignPlanData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign_id)
    if brief is None:
        raise ValidationError("Campaign brief is required before plan generation", code="BRIEF_REQUIRED")
    _, contexts = rag_pipeline.retrieve_and_save_contexts(
        db,
        campaign_id=campaign_id,
        used_for="PLAN_GENERATION",
        top_k=top_k,
    )
    brief_payload = brief_data_from_model(brief).model_dump(mode="json")
    result = llm_client.generate_campaign_plan(
        campaign_name=campaign.campaign_name,
        brief=brief_payload,
        rag_context=rag_pipeline.chunks_to_prompt_context(contexts),
    )
    trace_service.record_llm_success(
        db,
        campaign_id=campaign_id,
        operation_name="campaign_plan_generation",
        result=result,
        metadata={"context_count": len(contexts)},
    )
    db.commit()
    return CampaignPlanData(campaign_id=campaign_id, plan=result.data.get("plan", {}), retrieved_contexts=contexts)


def get_compliance_summary(db: Session, campaign_id: str) -> CampaignComplianceSummaryData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    variants = variant_repository.list_variants(db, campaign_id)
    latest_results = compliance_repository.latest_results_for_campaign(db, campaign_id)
    items: list[VariantComplianceSummaryItem] = []
    for variant in variants:
        latest = latest_results.get(variant.id)
        approval = approval_repository.latest_approval_for_variant(db, variant.id)
        items.append(
            VariantComplianceSummaryItem(
                variant_id=variant.id,
                variant_name=variant.variant_name,
                channel=variant.channel,
                variant_status=variant.status,
                risk_level=variant.risk_level,
                latest_compliance_status=latest.status if latest else None,
                latest_compliance_result_id=latest.id if latest else None,
                approval_status=approval.approval_status if approval else None,
            )
        )
    return CampaignComplianceSummaryData(
        campaign_id=campaign_id,
        variants_summary=items,
        total_variants=len(items),
        passed_count=sum(1 for item in items if item.latest_compliance_status == "PASSED"),
        warning_count=sum(1 for item in items if item.latest_compliance_status == "WARNING"),
        failed_count=sum(1 for item in items if item.latest_compliance_status == "FAILED"),
        approved_count=sum(1 for item in items if item.variant_status == "APPROVED"),
        rejected_count=sum(1 for item in items if item.variant_status == "REJECTED"),
    )


def _campaign_detail(campaign: Any) -> CampaignDetailData:
    brief = campaign.brief
    return CampaignDetailData(
        campaign_id=campaign.id,
        campaign_name=campaign.campaign_name,
        goal=brief.goal if brief else campaign.goal,
        target_audience=brief.target_audience if brief else None,
        offer_details=brief.offer_details if brief else None,
        tone=brief.tone if brief else None,
        preferred_channels=brief.preferred_channels if brief else [],
        cta_link=brief.cta_link if brief else None,
        expiry_date=brief.expiry_date if brief else None,
        status=campaign.status,
        brief_status=brief.brief_status if brief else None,
        missing_fields=brief.missing_fields if brief else [],
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


def brief_data_from_model(brief: Any) -> CampaignBriefData:
    return CampaignBriefData(
        goal=brief.goal,
        target_audience=brief.target_audience,
        offer_details=brief.offer_details,
        tone=brief.tone,
        preferred_channels=brief.preferred_channels or [],
        cta_link=brief.cta_link,
        expiry_date=brief.expiry_date,
        missing_fields=brief.missing_fields or [],
        brief_status=brief.brief_status,
    )


def _missing_fields(values: dict[str, Any]) -> list[str]:
    required = ["goal", "target_audience", "offer_details", "tone", "preferred_channels", "cta_link", "expiry_date"]
    return [field for field in required if not values.get(field)]
