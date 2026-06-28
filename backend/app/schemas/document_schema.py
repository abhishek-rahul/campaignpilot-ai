from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common_schema import Pagination


class DocumentData(BaseModel):
    document_id: str
    original_filename: str
    document_type: str
    status: str
    file_size_bytes: int
    content_type: str | None = None
    error_message: str | None = None
    chunks_count: int = 0
    embeddings_count: int = 0
    created_at: datetime
    ingested_at: datetime | None = None


class DocumentListData(BaseModel):
    items: list[DocumentData]
    pagination: Pagination


class IngestDocumentRequest(BaseModel):
    chunk_size: int = Field(default=1000, ge=200, le=4000)
    chunk_overlap: int = Field(default=150, ge=0, le=1000)
    embedding_model: str | None = None


class IngestDocumentData(BaseModel):
    document_id: str
    status: str
    chunks_count: int
    embeddings_count: int
    elasticsearch_index: str
    used_mock_embeddings: bool
