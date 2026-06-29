from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GeneratePayloadsRequest(BaseModel):
    channels: list[str] = Field(default_factory=list)
    regenerate: bool = False


class PayloadData(BaseModel):
    payload_id: str
    campaign_id: str
    variant_id: str
    channel: str
    payload_type: str
    payload_json: dict[str, Any]
    preview_text: str
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class GeneratePayloadsData(BaseModel):
    campaign_id: str
    selected_variant_id: str
    payloads: list[PayloadData]


class PayloadListData(BaseModel):
    campaign_id: str
    payloads: list[PayloadData]


class PayloadReadinessData(BaseModel):
    campaign_id: str
    ready: bool
    campaign_status: str | None = None
    selected_variant_id: str | None = None
    selected_variant_status: str | None = None
    missing_requirements: list[str] = Field(default_factory=list)


class ChannelCapabilityData(BaseModel):
    channel: str
    display_name: str
    is_active: bool = True
    supports_payload_generation: bool = True
    supports_send: bool = False
    payload_type: str


class ChannelListData(BaseModel):
    channels: list[ChannelCapabilityData]
