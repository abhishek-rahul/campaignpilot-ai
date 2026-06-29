from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DeliveryLog(Base):
    __tablename__ = "delivery_logs"
    __table_args__ = (
        Index("ix_delivery_logs_campaign_id", "campaign_id"),
        Index("ix_delivery_logs_variant_id", "variant_id"),
        Index("ix_delivery_logs_payload_id", "payload_id"),
        Index("ix_delivery_logs_channel", "channel"),
        Index("ix_delivery_logs_status", "status"),
        Index("ix_delivery_logs_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(50), ForeignKey("message_variants.id"), nullable=False)
    payload_id: Mapped[str] = mapped_column(String(50), ForeignKey("channel_payloads.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(150))
    request_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    response_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
