from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RetrievedContext(Base):
    __tablename__ = "retrieved_contexts"
    __table_args__ = (
        Index("ix_retrieved_contexts_campaign_id", "campaign_id"),
        Index("ix_retrieved_contexts_used_for", "used_for"),
        Index("ix_retrieved_contexts_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    document_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("brand_documents.id"))
    chunk_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("document_chunks.id"))
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_text: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="document_chunk")
    used_for: Mapped[str] = mapped_column(String(50), nullable=False)
    context_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
