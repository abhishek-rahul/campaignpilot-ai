from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DeliveryLogData(BaseModel):
    delivery_id: str
    payload_id: str
    campaign_id: str
    variant_id: str
    channel: str
    status: str
    provider: str
    provider_message_id: str | None = None
    request_json: dict[str, Any] | None = None
    response_json: dict[str, Any] | None = None
    error_message: str | None = None
    sent_at: datetime | None = None
    created_at: datetime


class SendPayloadData(BaseModel):
    delivery_id: str
    payload_id: str
    campaign_id: str
    variant_id: str
    channel: str
    status: str
    provider: str
    provider_message_id: str | None = None
    error_message: str | None = None
    sent_at: datetime | None = None
    created_at: datetime


class DeliveryLogListData(BaseModel):
    campaign_id: str
    delivery_logs: list[DeliveryLogData]
