from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BrandDocument(Base):
    __tablename__ = "brand_documents"
    __table_args__ = (
        Index("ix_brand_documents_campaign_id", "campaign_id"),
        Index("ix_brand_documents_status", "status"),
        Index("ix_brand_documents_document_type", "document_type"),
        Index("ix_brand_documents_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("campaigns.id"))
    uploaded_by: Mapped[str | None] = mapped_column(String(50), ForeignKey("campaign_managers.id"))
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120))
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="UPLOADED")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    embedding_records = relationship("EmbeddingRecord", back_populates="document", cascade="all, delete-orphan")
