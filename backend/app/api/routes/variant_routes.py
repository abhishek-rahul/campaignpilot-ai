from fastapi import APIRouter, Request

from app.core.response import not_implemented_response

router = APIRouter(prefix="/variants", tags=["variants"])


@router.patch("/{variant_id}")
def update_variant(variant_id: str, request: Request):
    return not_implemented_response("Slice 1/5 - Update Variant", request)


@router.post("/{variant_id}/compliance-check")
def run_variant_compliance_check(variant_id: str, request: Request):
    return not_implemented_response("Slice 3 - Run Variant Compliance Check", request)


@router.post("/{variant_id}/approve")
def approve_variant(variant_id: str, request: Request):
    return not_implemented_response("Slice 3 - Approve Variant", request)


@router.post("/{variant_id}/reject")
def reject_variant(variant_id: str, request: Request):
    return not_implemented_response("Slice 3 - Reject Variant", request)
