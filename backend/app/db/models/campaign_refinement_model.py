from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CampaignRefinement(Base):
    __tablename__ = "campaign_refinements"
    __table_args__ = (
        Index("ix_campaign_refinements_campaign_id", "campaign_id"),
        Index("ix_campaign_refinements_source_type", "source_type"),
        Index("ix_campaign_refinements_source_id", "source_id"),
        Index("ix_campaign_refinements_refinement_type", "refinement_type"),
        Index("ix_campaign_refinements_status", "status"),
        Index("ix_campaign_refinements_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(50))
    refinement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    before_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    after_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    llm_trace_id: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
