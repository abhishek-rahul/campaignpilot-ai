from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class GenerateVariantsRequest(BaseModel):
    variant_count: int = Field(default=3, ge=3, le=5)
    channels: list[str] | None = None
    use_rag_context: bool = False
    use_memory: bool = False


class VariantData(BaseModel):
    variant_id: str
    variant_name: str
    channel: str
    message_body: str
    tone: str | None = None
    reason: str | None = None
    risk_level: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GenerateVariantsData(BaseModel):
    campaign_id: str
    variants: list[VariantData]


class VariantListData(BaseModel):
    campaign_id: str
    variants: list[VariantData]


class UpdateVariantRequest(BaseModel):
    variant_name: str | None = None
    message_body: str | None = None
    tone: str | None = None
    reason: str | None = None
    risk_level: str | None = None


class VariantUpdateData(BaseModel):
    variant_id: str
    updated_fields: list[str]
    status: str
    updated_at: datetime
