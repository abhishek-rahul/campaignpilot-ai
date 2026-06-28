from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import CampaignBrief
from app.db.repositories import document_repository
from app.rag.embedding_client import embed_query
from app.rag.vector_store import search_chunks


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str | None
    chunk_id: str | None
    retrieved_text: str
    score: float | None
    rank_position: int
    metadata: dict[str, Any] = field(default_factory=dict)


def build_campaign_query(brief: CampaignBrief) -> str:
    parts = [
        brief.goal,
        brief.target_audience,
        brief.offer_details,
        brief.tone,
        " ".join(brief.preferred_channels or []),
    ]
    return " ".join(part for part in parts if part).strip() or "campaign brand guidelines"


def retrieve_for_campaign(db: Session, *, campaign_id: str, brief: CampaignBrief, top_k: int = 5) -> tuple[str, list[RetrievedChunk]]:
    query_text = build_campaign_query(brief)
    embedding = embed_query(query_text)
    try:
        results = search_chunks(
            query_text=query_text,
            query_vector=embedding.embeddings[0],
            campaign_id=campaign_id,
            top_k=top_k,
        )
        chunks = [
            RetrievedChunk(
                document_id=result.get("document_id"),
                chunk_id=result.get("chunk_id"),
                retrieved_text=result.get("retrieved_text", ""),
                score=result.get("score"),
                rank_position=index + 1,
                metadata=result.get("metadata") or {},
            )
            for index, result in enumerate(results)
            if result.get("retrieved_text")
        ]
        if chunks:
            return query_text, chunks
    except Exception:
        pass
    return query_text, _lexical_db_fallback(db, campaign_id=campaign_id, query_text=query_text, top_k=top_k)


def _lexical_db_fallback(db: Session, *, campaign_id: str, query_text: str, top_k: int) -> list[RetrievedChunk]:
    query_terms = {term.lower().strip(".,:;!?()[]") for term in query_text.split() if len(term) > 2}
    scored: list[tuple[int, Any]] = []
    for chunk in document_repository.list_ingested_chunks_for_campaign(db, campaign_id, limit=200):
        text_terms = set(chunk.chunk_text.lower().split())
        score = len(query_terms.intersection(text_terms))
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (-item[0], item[1].chunk_index))
    return [
        RetrievedChunk(
            document_id=chunk.document_id,
            chunk_id=chunk.id,
            retrieved_text=chunk.chunk_text,
            score=float(score),
            rank_position=index + 1,
            metadata=chunk.chunk_metadata,
        )
        for index, (score, chunk) in enumerate(scored[:top_k])
    ]
