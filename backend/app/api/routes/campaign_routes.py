from fastapi import APIRouter, Request

from app.core.response import not_implemented_response

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("")
def create_campaign(request: Request):
    return not_implemented_response("Slice 1 - Create Campaign", request)


@router.get("")
def list_campaigns(request: Request):
    return not_implemented_response("Slice 1 - List Campaigns", request)


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, request: Request):
    return not_implemented_response("Slice 1 - Get Campaign", request)


@router.patch("/{campaign_id}")
def update_campaign(campaign_id: str, request: Request):
    return not_implemented_response("Slice 1 - Update Campaign", request)


@router.get("/{campaign_id}/conversation")
def get_conversation(campaign_id: str, request: Request):
    return not_implemented_response("Slice 1 - Get Campaign Conversation", request)


@router.post("/{campaign_id}/plan")
def generate_campaign_plan(campaign_id: str, request: Request):
    return not_implemented_response("Slice 2 - Generate Campaign Plan", request)


@router.post("/{campaign_id}/generate-variants")
def generate_variants(campaign_id: str, request: Request):
    return not_implemented_response("Slice 1 - Generate Message Variants", request)


@router.get("/{campaign_id}/variants")
def list_variants(campaign_id: str, request: Request):
    return not_implemented_response("Slice 1 - List Message Variants", request)


@router.get("/{campaign_id}/retrieved-context")
def get_retrieved_context(campaign_id: str, request: Request):
    return not_implemented_response("Slice 2 - Get Retrieved Context", request)


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
