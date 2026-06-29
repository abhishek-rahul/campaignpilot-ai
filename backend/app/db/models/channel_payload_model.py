from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChannelPayload(Base):
    __tablename__ = "channel_payloads"
    __table_args__ = (
        Index("ix_channel_payloads_campaign_id", "campaign_id"),
        Index("ix_channel_payloads_variant_id", "variant_id"),
        Index("ix_channel_payloads_channel", "channel"),
        Index("ix_channel_payloads_status", "status"),
        Index("ix_channel_payloads_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(50), ForeignKey("message_variants.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    payload_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    preview_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERATED")
    generated_by: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
