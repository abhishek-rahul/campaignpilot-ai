from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = (
        Index("ix_campaigns_created_by", "created_by"),
        Index("ix_campaigns_status", "status"),
        Index("ix_campaigns_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_name: Mapped[str] = mapped_column(String(200), nullable=False)
    goal: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    created_by: Mapped[str | None] = mapped_column(String(50), ForeignKey("campaign_managers.id"))
    selected_variant_id: Mapped[str | None] = mapped_column(String(50))
    campaign_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    manager = relationship("CampaignManager", back_populates="campaigns")
    brief = relationship("CampaignBrief", back_populates="campaign", uselist=False, cascade="all, delete-orphan")
    messages = relationship("ConversationMessage", back_populates="campaign", cascade="all, delete-orphan")
    variants = relationship("MessageVariant", back_populates="campaign", cascade="all, delete-orphan")
    traces = relationship("LLMTrace", back_populates="campaign", cascade="all, delete-orphan")
