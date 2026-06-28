from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common_schema import Pagination


class CampaignBriefData(BaseModel):
    goal: str | None = None
    target_audience: str | None = None
    offer_details: str | None = None
    tone: str | None = None
    preferred_channels: list[str] = Field(default_factory=list)
    cta_link: str | None = None
    expiry_date: date | None = None
    missing_fields: list[str] = Field(default_factory=list)
    brief_status: str = "INCOMPLETE"


class CreateCampaignRequest(BaseModel):
    campaign_name: str
    goal: str | None = None
    target_audience: str | None = None
    offer_details: str | None = None
    tone: str | None = None
    preferred_channels: list[str] = Field(default_factory=list)
    cta_link: str | None = None
    expiry_date: date | None = None


class UpdateCampaignRequest(BaseModel):
    campaign_name: str | None = None
    goal: str | None = None
    target_audience: str | None = None
    offer_details: str | None = None
    tone: str | None = None
    preferred_channels: list[str] | None = None
    cta_link: str | None = None
    expiry_date: date | None = None


class CampaignCreateData(BaseModel):
    campaign_id: str
    campaign_name: str
    status: str
    created_at: datetime


class CampaignListItem(BaseModel):
    campaign_id: str
    campaign_name: str
    status: str
    created_at: datetime


class CampaignListData(BaseModel):
    items: list[CampaignListItem]
    pagination: Pagination


class CampaignDetailData(BaseModel):
    campaign_id: str
    campaign_name: str
    goal: str | None = None
    target_audience: str | None = None
    offer_details: str | None = None
    tone: str | None = None
    preferred_channels: list[str] = Field(default_factory=list)
    cta_link: str | None = None
    expiry_date: date | None = None
    status: str
    brief_status: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class CampaignUpdateData(BaseModel):
    campaign_id: str
    updated_fields: list[str]
    status: str
    updated_at: datetime
