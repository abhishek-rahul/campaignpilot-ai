from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import not_implemented_response, success_response
from app.schemas.variant_schema import UpdateVariantRequest
from app.services import variant_service

router = APIRouter(prefix="/variants", tags=["variants"])


@router.patch("/{variant_id}")
def update_variant(variant_id: str, payload: UpdateVariantRequest, request: Request, db: Session = Depends(get_db)):
    data = variant_service.update_variant(db, variant_id, payload)
    return success_response("Variant updated successfully", data.model_dump(mode="json"), request)


@router.post("/{variant_id}/compliance-check")
def run_variant_compliance_check(variant_id: str, request: Request):
    return not_implemented_response("Slice 3 - Run Variant Compliance Check", request)


@router.post("/{variant_id}/approve")
def approve_variant(variant_id: str, request: Request):
    return not_implemented_response("Slice 3 - Approve Variant", request)


@router.post("/{variant_id}/reject")
def reject_variant(variant_id: str, request: Request):
    return not_implemented_response("Slice 3 - Reject Variant", request)
