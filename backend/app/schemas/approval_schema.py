from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ApproveVariantRequest(BaseModel):
    reason: str | None = None
    allow_high_risk_override: bool = False


class RejectVariantRequest(BaseModel):
    reason: str | None = None


class ApprovalActionData(BaseModel):
    variant_id: str
    campaign_id: str
    status: str
    approval_action_id: str
    previous_status: str
    new_status: str
    reason: str | None = None
    override_used: bool = False
    created_at: datetime
