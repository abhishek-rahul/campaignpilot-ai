from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmbeddingRecord(Base):
    __tablename__ = "embedding_records"
    __table_args__ = (
        Index("ix_embedding_records_document_id", "document_id"),
        Index("ix_embedding_records_chunk_id", "chunk_id"),
        Index("ix_embedding_records_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("brand_documents.id"), nullable=False)
    chunk_id: Mapped[str] = mapped_column(String(50), ForeignKey("document_chunks.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    vector_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    elasticsearch_index: Mapped[str] = mapped_column(String(150), nullable=False)
    elasticsearch_document_id: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="INDEXED")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("BrandDocument", back_populates="embedding_records")
    chunk = relationship("DocumentChunk", back_populates="embedding_records")
