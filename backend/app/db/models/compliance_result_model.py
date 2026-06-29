from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ComplianceResult(Base):
    __tablename__ = "compliance_results"
    __table_args__ = (
        Index("ix_compliance_results_campaign_id", "campaign_id"),
        Index("ix_compliance_results_variant_id", "variant_id"),
        Index("ix_compliance_results_status", "status"),
        Index("ix_compliance_results_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(50), ForeignKey("message_variants.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    issues_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    checked_rules_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    source_context_ids_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    raw_result_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
