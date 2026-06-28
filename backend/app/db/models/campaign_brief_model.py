from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CampaignBrief(Base):
    __tablename__ = "campaign_briefs"
    __table_args__ = (Index("ix_campaign_briefs_campaign_id", "campaign_id"),)

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False, unique=True)
    goal: Mapped[str | None] = mapped_column(Text)
    target_audience: Mapped[str | None] = mapped_column(String(150))
    offer_details: Mapped[str | None] = mapped_column(Text)
    tone: Mapped[str | None] = mapped_column(String(100))
    preferred_channels: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    cta_link: Mapped[str | None] = mapped_column(Text)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    missing_fields: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    brief_status: Mapped[str] = mapped_column(String(50), nullable=False, default="INCOMPLETE")
    raw_user_input: Mapped[str | None] = mapped_column(Text)
    structured_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    campaign = relationship("Campaign", back_populates="brief")
