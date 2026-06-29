from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import not_implemented_response, success_response
from app.schemas.campaign_schema import CreateCampaignRequest, UpdateCampaignRequest
from app.schemas.payload_schema import GeneratePayloadsRequest
from app.schemas.refinement_schema import RefineBriefRequest, RegenerateVariantsRequest
from app.schemas.variant_schema import GenerateVariantsRequest
from app.services import (
    campaign_service,
    channel_service,
    chat_service,
    delivery_service,
    evaluation_service,
    observability_service,
    refinement_service,
    variant_service,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("")
def create_campaign(payload: CreateCampaignRequest, request: Request, db: Session = Depends(get_db)):
    data = campaign_service.create_campaign(db, payload)
    return success_response("Campaign created successfully", data.model_dump(mode="json"), request)


@router.get("")
def list_campaigns(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    data = campaign_service.list_campaigns(db, page=page, page_size=page_size, status=status)
    return success_response("Campaigns fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = campaign_service.get_campaign_detail(db, campaign_id)
    return success_response("Campaign fetched successfully", data.model_dump(mode="json"), request)


@router.patch("/{campaign_id}")
def update_campaign(campaign_id: str, payload: UpdateCampaignRequest, request: Request, db: Session = Depends(get_db)):
    data = campaign_service.update_campaign(db, campaign_id, payload)
    return success_response("Campaign updated successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/conversation")
def get_conversation(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = chat_service.get_conversation(db, campaign_id)
    return success_response("Conversation fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/observability-summary")
def get_observability_summary(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = observability_service.get_campaign_summary(db, campaign_id)
    return success_response("Campaign observability summary fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/debug-timeline")
def get_debug_timeline(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = observability_service.get_debug_timeline(db, campaign_id)
    return success_response("Campaign debug timeline fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/evaluations")
def list_campaign_evaluations(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    evaluation_type: str | None = None,
    variant_id: str | None = None,
):
    data = evaluation_service.list_campaign_evaluations(
        db,
        campaign_id,
        evaluation_type=evaluation_type,
        variant_id=variant_id,
    )
    return success_response("Campaign evaluations fetched successfully", data.model_dump(mode="json"), request)


@router.post("/{campaign_id}/evaluate-readiness")
def evaluate_campaign_readiness(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = evaluation_service.evaluate_campaign_readiness(db, campaign_id)
    return success_response("Campaign readiness evaluation completed successfully", data.model_dump(mode="json"), request)


@router.post("/{campaign_id}/refine-brief")
def refine_campaign_brief(
    campaign_id: str,
    payload: RefineBriefRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = refinement_service.refine_brief(db, campaign_id, payload)
    return success_response("Campaign brief refinement generated successfully", data.model_dump(mode="json"), request)


@router.post("/{campaign_id}/regenerate-variants")
def regenerate_variants(
    campaign_id: str,
    payload: RegenerateVariantsRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = refinement_service.regenerate_variants(db, campaign_id, payload)
    return success_response("Message variants regenerated successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/refinements")
def list_campaign_refinements(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    refinement_type: str | None = None,
    source_type: str | None = None,
):
    data = refinement_service.list_refinements(
        db,
        campaign_id,
        refinement_type=refinement_type,
        source_type=source_type,
    )
    return success_response("Campaign refinements fetched successfully", data.model_dump(mode="json"), request)


@router.post("/{campaign_id}/plan")
def generate_campaign_plan(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    top_k: int = Query(5, ge=1, le=10),
):
    data = campaign_service.generate_campaign_plan(db, campaign_id, top_k=top_k)
    return success_response("Campaign plan generated successfully", data.model_dump(mode="json"), request)


@router.post("/{campaign_id}/generate-variants")
def generate_variants(
    campaign_id: str,
    payload: GenerateVariantsRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = variant_service.generate_variants(db, campaign_id, payload)
    return success_response("Message variants generated successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/variants")
def list_variants(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = variant_service.list_variants(db, campaign_id)
    return success_response("Message variants fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/retrieved-context")
def get_retrieved_context(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    refresh: bool = False,
    top_k: int = Query(5, ge=1, le=10),
):
    data = campaign_service.get_retrieved_context(db, campaign_id, refresh=refresh, top_k=top_k)
    return success_response("Retrieved context fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/compliance-summary")
def get_compliance_summary(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = campaign_service.get_compliance_summary(db, campaign_id)
    return success_response("Campaign compliance summary fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/payload-readiness")
def get_payload_readiness(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    data = channel_service.get_payload_readiness(db, campaign_id)
    return success_response("Payload readiness fetched successfully", data.model_dump(mode="json"), request)


@router.post("/{campaign_id}/payloads")
def generate_payloads(
    campaign_id: str,
    payload: GeneratePayloadsRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = channel_service.generate_payloads(db, campaign_id, payload)
    return success_response("Channel payloads generated successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/payloads")
def list_payloads(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    channel: str | None = None,
    status: str | None = None,
):
    data = channel_service.list_payloads(db, campaign_id, channel=channel, status=status)
    return success_response("Channel payloads fetched successfully", data.model_dump(mode="json"), request)


@router.post("/{campaign_id}/send")
def send_campaign(campaign_id: str, request: Request):
    return not_implemented_response("Slice 4 - Send Campaign", request)


@router.get("/{campaign_id}/delivery-logs")
def get_delivery_logs(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    channel: str | None = None,
    status: str | None = None,
):
    data = delivery_service.list_delivery_logs(db, campaign_id, channel=channel, status=status)
    return success_response("Delivery logs fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/llm-traces")
def get_llm_traces(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    operation_name: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=100),
):
    data = observability_service.list_campaign_llm_traces(
        db,
        campaign_id,
        operation_name=operation_name,
        status=status,
        limit=limit,
    )
    return success_response("LLM traces fetched successfully", data.model_dump(mode="json"), request)


@router.get("/{campaign_id}/tool-calls")
def get_tool_calls(
    campaign_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tool_name: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=100),
):
    data = observability_service.list_campaign_tool_calls(
        db,
        campaign_id,
        tool_name=tool_name,
        status=status,
        limit=limit,
    )
    return success_response("Tool call logs fetched successfully", data.model_dump(mode="json"), request)
