from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.campaign_schema import CampaignBriefData
from app.schemas.variant_schema import VariantData


class RefineBriefRequest(BaseModel):
    feedback: str = Field(min_length=1)
    use_rag_context: bool = True
    apply: bool = True


class RefineVariantRequest(BaseModel):
    feedback: str = Field(min_length=1)
    use_rag_context: bool = True
    create_new_variant: bool = True


class RegenerateVariantsRequest(BaseModel):
    feedback: str = Field(min_length=1)
    variant_count: int = Field(default=3, ge=3, le=5)
    channels: list[str] | None = None
    use_rag_context: bool = True


class RefinementData(BaseModel):
    refinement_id: str
    campaign_id: str
    source_type: str
    source_id: str | None = None
    refinement_type: str
    user_feedback: str
    before_json: dict[str, Any]
    after_json: dict[str, Any]
    status: str
    llm_trace_id: str | None = None
    created_at: datetime


class RefineBriefData(BaseModel):
    campaign_id: str
    refinement_id: str
    applied: bool
    before_brief: CampaignBriefData
    after_brief: CampaignBriefData
    campaign_status: str
    selected_variant_id: str | None = None


class RefineVariantData(BaseModel):
    campaign_id: str
    source_variant_id: str
    refined_variant: VariantData
    refinement_id: str
    requires_compliance_check: bool = True


class RegenerateVariantsData(BaseModel):
    campaign_id: str
    refinement_id: str
    variants: list[VariantData]
    requires_compliance_check: bool = True


class RefinementListData(BaseModel):
    campaign_id: str
    refinements: list[RefinementData]
