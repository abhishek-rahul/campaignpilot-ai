from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, document_repository
from app.rag.document_loader import load_document_text, validate_supported_file
from app.rag.embedding_client import embed_texts
from app.rag.text_splitter import split_text
from app.rag.vector_store import index_chunks
from app.schemas.common_schema import Pagination
from app.schemas.document_schema import DocumentData, DocumentListData, IngestDocumentData, IngestDocumentRequest


async def upload_document(
    db: Session,
    *,
    file: UploadFile,
    document_type: str,
    campaign_id: str | None = None,
) -> DocumentData:
    filename = (file.filename or "").strip()
    if not filename:
        raise ValidationError("Filename is required")
    validate_supported_file(filename)
    if campaign_id and campaign_repository.get_campaign(db, campaign_id) is None:
        raise ResourceNotFoundError("Campaign not found")

    campaign_repository.ensure_default_manager(db)
    document_id = new_id("doc")
    extension = Path(filename).suffix.lower()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{document_id}{extension}"
    file_path = upload_dir / stored_filename

    with file_path.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    size = file_path.stat().st_size
    document = document_repository.create_document(
        db,
        document_id=document_id,
        campaign_id=campaign_id,
        uploaded_by=campaign_repository.DEFAULT_MANAGER_ID,
        original_filename=filename,
        stored_filename=stored_filename,
        file_path=str(file_path),
        content_type=file.content_type,
        file_size_bytes=size,
        document_type=document_type.strip() or "brand_guideline",
    )
    db.commit()
    db.refresh(document)
    return _document_data(db, document)


def list_documents(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    document_type: str | None = None,
    campaign_id: str | None = None,
) -> DocumentListData:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    documents, total = document_repository.list_documents(
        db,
        page=page,
        page_size=page_size,
        status=status,
        document_type=document_type,
        campaign_id=campaign_id,
    )
    return DocumentListData(
        items=[_document_data(db, document) for document in documents],
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=campaign_repository.count_total_pages(total, page_size),
        ),
    )


def get_document(db: Session, document_id: str) -> DocumentData:
    document = document_repository.get_document(db, document_id)
    if document is None:
        raise ResourceNotFoundError("Document not found")
    return _document_data(db, document)


def ingest_document(db: Session, document_id: str, request: IngestDocumentRequest) -> IngestDocumentData:
    document = document_repository.get_document(db, document_id)
    if document is None:
        raise ResourceNotFoundError("Document not found")

    try:
        document_repository.mark_document_status(db, document, "INGESTING")
        document_repository.delete_document_processing_rows(db, document.id)
        text = load_document_text(document.file_path)
        chunks = split_text(text, chunk_size=request.chunk_size, chunk_overlap=request.chunk_overlap)
        if not chunks:
            raise ValidationError("Document did not produce chunks", code="EMPTY_DOCUMENT")

        chunk_rows = document_repository.create_chunks(
            db,
            [
                {
                    "id": new_id("chunk"),
                    "document_id": document.id,
                    "chunk_index": chunk.chunk_index,
                    "chunk_text": chunk.chunk_text,
                    "token_count": chunk.token_count,
                    "chunk_metadata": {
                        "source_filename": document.original_filename,
                        "document_type": document.document_type,
                    },
                }
                for chunk in chunks
            ],
        )
        embedding_result = embed_texts([chunk.chunk_text for chunk in chunk_rows], model_name=request.embedding_model)
        es_documents = []
        for chunk, vector in zip(chunk_rows, embedding_result.embeddings, strict=True):
            es_doc_id = f"{document.id}_{chunk.id}"
            es_documents.append(
                {
                    "id": es_doc_id,
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "campaign_id": document.campaign_id or "__global__",
                    "document_type": document.document_type,
                    "source_filename": document.original_filename,
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.chunk_metadata,
                    "embedding": vector,
                    "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
                }
            )

        indexing_error: str | None = None
        indexed_ids: list[str] = []
        try:
            indexed_ids = index_chunks(
                documents=es_documents,
                vector_dimension=embedding_result.vector_dimension,
                index_name=settings.elasticsearch_document_index,
            )
        except Exception as exc:  # noqa: BLE001
            indexing_error = f"Elasticsearch indexing skipped: {exc.__class__.__name__}"

        records = []
        for chunk, es_document in zip(chunk_rows, es_documents, strict=True):
            es_id = es_document["id"] if es_document["id"] in indexed_ids else None
            chunk.elasticsearch_doc_id = es_id
            records.append(
                {
                    "id": new_id("emb"),
                    "document_id": document.id,
                    "chunk_id": chunk.id,
                    "provider": embedding_result.provider,
                    "model_name": embedding_result.model_name,
                    "vector_dimension": embedding_result.vector_dimension,
                    "elasticsearch_index": settings.elasticsearch_document_index,
                    "elasticsearch_document_id": es_id,
                    "status": "INDEXED" if es_id else "EMBEDDED_NOT_INDEXED",
                    "error_message": indexing_error,
                }
            )
        document_repository.create_embedding_records(db, records)
        document_repository.mark_document_status(db, document, "INGESTED", error_message=indexing_error)
        db.commit()
        db.refresh(document)
        return IngestDocumentData(
            document_id=document.id,
            status=document.status,
            chunks_count=document_repository.count_chunks(db, document.id),
            embeddings_count=document_repository.count_embeddings(db, document.id),
            elasticsearch_index=settings.elasticsearch_document_index,
            used_mock_embeddings=embedding_result.used_mock,
        )
    except Exception as exc:
        db.rollback()
        document = document_repository.get_document(db, document_id)
        if document is not None:
            document_repository.mark_document_status(db, document, "FAILED", error_message=str(exc))
            db.commit()
        if isinstance(exc, ValidationError):
            raise
        raise


def _document_data(db: Session, document) -> DocumentData:
    return DocumentData(
        document_id=document.id,
        original_filename=document.original_filename,
        document_type=document.document_type,
        status=document.status,
        file_size_bytes=document.file_size_bytes,
        content_type=document.content_type,
        error_message=document.error_message,
        chunks_count=document_repository.count_chunks(db, document.id),
        embeddings_count=document_repository.count_embeddings(db, document.id),
        created_at=document.created_at,
        ingested_at=document.ingested_at,
    )
