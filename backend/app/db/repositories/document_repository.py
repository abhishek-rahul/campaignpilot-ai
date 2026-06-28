from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import BrandDocument, DocumentChunk, EmbeddingRecord


def create_document(
    db: Session,
    *,
    document_id: str,
    campaign_id: str | None,
    uploaded_by: str | None,
    original_filename: str,
    stored_filename: str,
    file_path: str,
    content_type: str | None,
    file_size_bytes: int,
    document_type: str,
) -> BrandDocument:
    document = BrandDocument(
        id=document_id,
        campaign_id=campaign_id,
        uploaded_by=uploaded_by,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        content_type=content_type,
        file_size_bytes=file_size_bytes,
        document_type=document_type,
        status="UPLOADED",
    )
    db.add(document)
    db.flush()
    db.refresh(document)
    return document


def get_document(db: Session, document_id: str) -> BrandDocument | None:
    return db.get(BrandDocument, document_id)


def list_documents(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    document_type: str | None = None,
    campaign_id: str | None = None,
) -> tuple[list[BrandDocument], int]:
    stmt = select(BrandDocument)
    count_stmt = select(func.count()).select_from(BrandDocument)
    filters = []
    if status:
        filters.append(BrandDocument.status == status)
    if document_type:
        filters.append(BrandDocument.document_type == document_type)
    if campaign_id:
        filters.append(BrandDocument.campaign_id == campaign_id)
    for condition in filters:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    total = db.scalar(count_stmt) or 0
    documents = list(
        db.scalars(
            stmt.order_by(BrandDocument.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
    )
    return documents, total


def mark_document_status(db: Session, document: BrandDocument, status: str, error_message: str | None = None) -> BrandDocument:
    document.status = status
    document.error_message = error_message
    if status == "INGESTED":
        document.ingested_at = datetime.now(timezone.utc)
    db.flush()
    db.refresh(document)
    return document


def delete_document_processing_rows(db: Session, document_id: str) -> None:
    db.execute(delete(EmbeddingRecord).where(EmbeddingRecord.document_id == document_id))
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    db.flush()


def create_chunks(db: Session, chunks: Iterable[dict[str, Any]]) -> list[DocumentChunk]:
    models = [DocumentChunk(**chunk) for chunk in chunks]
    db.add_all(models)
    db.flush()
    for model in models:
        db.refresh(model)
    return models


def create_embedding_records(db: Session, records: Iterable[dict[str, Any]]) -> list[EmbeddingRecord]:
    models = [EmbeddingRecord(**record) for record in records]
    db.add_all(models)
    db.flush()
    for model in models:
        db.refresh(model)
    return models


def count_chunks(db: Session, document_id: str) -> int:
    return db.scalar(select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == document_id)) or 0


def count_embeddings(db: Session, document_id: str) -> int:
    return db.scalar(select(func.count()).select_from(EmbeddingRecord).where(EmbeddingRecord.document_id == document_id)) or 0


def list_ingested_chunks_for_campaign(db: Session, campaign_id: str | None, limit: int = 100) -> list[DocumentChunk]:
    stmt = (
        select(DocumentChunk)
        .join(BrandDocument, BrandDocument.id == DocumentChunk.document_id)
        .where(BrandDocument.status == "INGESTED")
        .order_by(BrandDocument.created_at.desc(), DocumentChunk.chunk_index.asc())
        .limit(limit)
    )
    if campaign_id:
        stmt = stmt.where((BrandDocument.campaign_id == campaign_id) | (BrandDocument.campaign_id.is_(None)))
    return list(db.scalars(stmt).all())
