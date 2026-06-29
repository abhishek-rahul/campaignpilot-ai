from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    __table_args__ = (
        Index("ix_evaluation_results_campaign_id", "campaign_id"),
        Index("ix_evaluation_results_variant_id", "variant_id"),
        Index("ix_evaluation_results_evaluation_type", "evaluation_type"),
        Index("ix_evaluation_results_grade", "grade"),
        Index("ix_evaluation_results_passed", "passed"),
        Index("ix_evaluation_results_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    variant_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("message_variants.id"))
    evaluation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[str] = mapped_column(String(5), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    checks_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
