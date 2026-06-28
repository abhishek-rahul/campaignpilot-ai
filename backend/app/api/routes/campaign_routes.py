from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import not_implemented_response, success_response
from app.schemas.campaign_schema import CreateCampaignRequest, UpdateCampaignRequest
from app.schemas.variant_schema import GenerateVariantsRequest
from app.services import campaign_service, chat_service, variant_service

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


@router.post("/{campaign_id}/payloads")
def generate_payloads(campaign_id: str, request: Request):
    return not_implemented_response("Slice 4 - Generate Channel Payloads", request)


@router.get("/{campaign_id}/payloads")
def list_payloads(campaign_id: str, request: Request):
    return not_implemented_response("Slice 4 - List Channel Payloads", request)


@router.post("/{campaign_id}/send")
def send_campaign(campaign_id: str, request: Request):
    return not_implemented_response("Slice 4 - Send Campaign", request)


@router.get("/{campaign_id}/delivery-logs")
def get_delivery_logs(campaign_id: str, request: Request):
    return not_implemented_response("Slice 4 - Get Delivery Logs", request)


@router.get("/{campaign_id}/llm-traces")
def get_llm_traces(campaign_id: str, request: Request):
    return not_implemented_response("Slice 6 - Get LLM Traces", request)


@router.get("/{campaign_id}/tool-calls")
def get_tool_calls(campaign_id: str, request: Request):
    return not_implemented_response("Slice 6 - Get Tool Calls", request)
