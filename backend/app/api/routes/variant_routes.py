from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.response import success_response
from app.schemas.approval_schema import ApproveVariantRequest, RejectVariantRequest
from app.schemas.compliance_schema import ComplianceCheckRequest
from app.schemas.refinement_schema import RefineVariantRequest
from app.schemas.variant_schema import UpdateVariantRequest
from app.services import approval_service, compliance_service, refinement_service, variant_service

router = APIRouter(prefix="/variants", tags=["variants"])


@router.patch("/{variant_id}")
def update_variant(variant_id: str, payload: UpdateVariantRequest, request: Request, db: Session = Depends(get_db)):
    data = variant_service.update_variant(db, variant_id, payload)
    return success_response("Variant updated successfully", data.model_dump(mode="json"), request)


@router.post("/{variant_id}/refine")
def refine_variant(
    variant_id: str,
    payload: RefineVariantRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = refinement_service.refine_variant(db, variant_id, payload)
    return success_response("Variant refinement generated successfully", data.model_dump(mode="json"), request)


@router.post("/{variant_id}/compliance-check")
def run_variant_compliance_check(
    variant_id: str,
    payload: ComplianceCheckRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = compliance_service.run_compliance_check(db, variant_id, payload)
    return success_response("Compliance check completed successfully", data.model_dump(mode="json"), request)


@router.get("/{variant_id}/compliance-checks")
def list_variant_compliance_checks(variant_id: str, request: Request, db: Session = Depends(get_db)):
    data = compliance_service.list_compliance_checks(db, variant_id)
    return success_response("Compliance checks fetched successfully", data.model_dump(mode="json"), request)


@router.post("/{variant_id}/approve")
def approve_variant(
    variant_id: str,
    payload: ApproveVariantRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = approval_service.approve_variant(db, variant_id, payload)
    return success_response("Variant approved successfully", data.model_dump(mode="json"), request)


@router.post("/{variant_id}/reject")
def reject_variant(
    variant_id: str,
    payload: RejectVariantRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    data = approval_service.reject_variant(db, variant_id, payload)
    return success_response("Variant rejected successfully", data.model_dump(mode="json"), request)
