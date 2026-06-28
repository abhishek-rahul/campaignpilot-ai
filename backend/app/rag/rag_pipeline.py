from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, rag_repository
from app.rag.retriever import RetrievedChunk, retrieve_for_campaign
from app.schemas.rag_schema import RetrievedContextData


def retrieve_and_save_contexts(
    db: Session,
    *,
    campaign_id: str,
    used_for: str,
    top_k: int = 5,
) -> tuple[str, list[RetrievedContextData]]:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign_id)
    if brief is None:
        raise ValidationError("Campaign brief is required before retrieving context", code="BRIEF_REQUIRED")

    query_text, chunks = retrieve_for_campaign(db, campaign_id=campaign_id, brief=brief, top_k=top_k)
    rows = rag_repository.create_retrieved_contexts(
        db,
        [
            {
                "id": new_id("ctx"),
                "campaign_id": campaign_id,
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "query_text": query_text,
                "retrieved_text": chunk.retrieved_text,
                "score": chunk.score,
                "rank_position": chunk.rank_position,
                "source_type": "document_chunk",
                "used_for": used_for,
                "context_metadata": chunk.metadata,
            }
            for chunk in chunks
        ],
    )
    return query_text, [_context_data(row) for row in rows]


def list_saved_contexts(db: Session, *, campaign_id: str, used_for: str | None = None) -> list[RetrievedContextData]:
    return [_context_data(row) for row in rag_repository.list_retrieved_contexts(db, campaign_id, used_for=used_for)]


def chunks_to_prompt_context(chunks: list[RetrievedChunk] | list[RetrievedContextData]) -> list[dict]:
    return [
        {
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "text": chunk.retrieved_text,
            "score": chunk.score,
            "rank_position": chunk.rank_position,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]


def _context_data(row) -> RetrievedContextData:
    return RetrievedContextData(
        context_id=row.id,
        campaign_id=row.campaign_id,
        document_id=row.document_id,
        chunk_id=row.chunk_id,
        query_text=row.query_text,
        retrieved_text=row.retrieved_text,
        score=row.score,
        rank_position=row.rank_position,
        source_type=row.source_type,
        used_for=row.used_for,
        metadata=row.context_metadata or {},
        created_at=row.created_at,
    )
