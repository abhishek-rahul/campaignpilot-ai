from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import approval_repository, campaign_repository, compliance_repository, variant_repository
from app.schemas.approval_schema import ApprovalActionData, ApproveVariantRequest, RejectVariantRequest


def approve_variant(db: Session, variant_id: str, request: ApproveVariantRequest) -> ApprovalActionData:
    variant = variant_repository.get_variant(db, variant_id)
    if variant is None:
        raise ResourceNotFoundError("Variant not found")
    campaign = campaign_repository.get_campaign(db, variant.campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    latest = compliance_repository.latest_compliance_result(db, variant_id)
    if latest is None:
        raise ValidationError("Run compliance check before approval", code="COMPLIANCE_CHECK_REQUIRED")
    override_used = False
    if latest.status == "FAILED":
        if not request.allow_high_risk_override:
            raise ValidationError("Variant failed compliance check", code="VARIANT_NOT_COMPLIANT")
        override_used = True

    previous_status = variant.status
    variant_repository.update_variant_status(db, variant, "APPROVED")
    campaign_repository.select_variant(db, campaign, variant.id)
    campaign_repository.update_campaign_status(db, campaign, "APPROVED")
    approval = approval_repository.create_approval(
        db,
        {
            "id": new_id("appr"),
            "campaign_id": campaign.id,
            "variant_id": variant.id,
            "approval_status": "APPROVED",
            "reason": request.reason,
            "actor_id": None,
            "previous_status": previous_status,
            "new_status": "APPROVED",
            "override_used": override_used,
        },
    )
    db.commit()
    db.refresh(approval)
    return _approval_data(approval)


def reject_variant(db: Session, variant_id: str, request: RejectVariantRequest) -> ApprovalActionData:
    variant = variant_repository.get_variant(db, variant_id)
    if variant is None:
        raise ResourceNotFoundError("Variant not found")
    campaign = campaign_repository.get_campaign(db, variant.campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    previous_status = variant.status
    variant_repository.update_variant_status(db, variant, "REJECTED")
    approval = approval_repository.create_approval(
        db,
        {
            "id": new_id("appr"),
            "campaign_id": campaign.id,
            "variant_id": variant.id,
            "approval_status": "REJECTED",
            "reason": request.reason,
            "actor_id": None,
            "previous_status": previous_status,
            "new_status": "REJECTED",
            "override_used": False,
        },
    )
    db.commit()
    db.refresh(approval)
    return _approval_data(approval)


def _approval_data(approval) -> ApprovalActionData:
    return ApprovalActionData(
        variant_id=approval.variant_id,
        campaign_id=approval.campaign_id,
        status=approval.approval_status,
        approval_action_id=approval.id,
        previous_status=approval.previous_status,
        new_status=approval.new_status,
        reason=approval.reason,
        override_used=approval.override_used,
        created_at=approval.created_at,
    )
