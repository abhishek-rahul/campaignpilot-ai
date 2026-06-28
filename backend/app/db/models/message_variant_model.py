from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MessageVariant(Base):
    __tablename__ = "message_variants"
    __table_args__ = (
        Index("ix_message_variants_campaign_id", "campaign_id"),
        Index("ix_message_variants_channel", "channel"),
        Index("ix_message_variants_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    variant_name: Mapped[str] = mapped_column(String(150), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str | None] = mapped_column(String(100))
    reason: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERATED")
    context_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    campaign = relationship("Campaign", back_populates="variants")
