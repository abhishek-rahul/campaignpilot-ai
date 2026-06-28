from __future__ import annotations

from typing import Any

from app.core.config import settings


def index_chunks(
    *,
    documents: list[dict[str, Any]],
    vector_dimension: int,
    index_name: str | None = None,
) -> list[str]:
    index = index_name or settings.elasticsearch_document_index
    client = _client()
    _ensure_index(client, index, vector_dimension)
    indexed_ids: list[str] = []
    for document in documents:
        doc_id = document["id"]
        client.index(index=index, id=doc_id, document=document)
        indexed_ids.append(doc_id)
    return indexed_ids


def search_chunks(
    *,
    query_text: str,
    query_vector: list[float],
    campaign_id: str | None,
    top_k: int,
    index_name: str | None = None,
) -> list[dict[str, Any]]:
    index = index_name or settings.elasticsearch_document_index
    client = _client()
    try:
        query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": _campaign_filter(campaign_id),
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_vector},
                    },
                }
            },
        }
        response = client.search(index=index, body=query)
    except Exception:
        response = client.search(
            index=index,
            body={
                "size": top_k,
                "query": {
                    "bool": {
                        "must": [{"match": {"chunk_text": query_text}}],
                        "filter": _campaign_terms(campaign_id),
                    }
                },
            },
        )
    return [_hit_to_result(hit) for hit in response.get("hits", {}).get("hits", [])]


def _client():
    from elasticsearch import Elasticsearch

    return Elasticsearch(settings.elasticsearch_url)


def _ensure_index(client: Any, index: str, vector_dimension: int) -> None:
    if client.indices.exists(index=index):
        current_dimension = _current_embedding_dimension(client, index)
        if current_dimension == vector_dimension:
            return
        client.indices.delete(index=index)
    client.indices.create(
        index=index,
        mappings={
            "properties": {
                "chunk_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "campaign_id": {"type": "keyword"},
                "document_type": {"type": "keyword"},
                "source_filename": {"type": "keyword"},
                "chunk_text": {"type": "text"},
                "chunk_index": {"type": "integer"},
                "metadata": {"type": "object", "enabled": True},
                "embedding": {"type": "dense_vector", "dims": vector_dimension, "index": False},
                "created_at": {"type": "date"},
            }
        },
    )


def _current_embedding_dimension(client: Any, index: str) -> int | None:
    mapping = client.indices.get_mapping(index=index)
    index_mapping = mapping.get(index, {})
    properties = index_mapping.get("mappings", {}).get("properties", {})
    embedding = properties.get("embedding", {})
    return embedding.get("dims")


def _campaign_filter(campaign_id: str | None) -> dict[str, Any]:
    filters = _campaign_terms(campaign_id)
    return {"bool": {"filter": filters}} if filters else {"match_all": {}}


def _campaign_terms(campaign_id: str | None) -> list[dict[str, Any]]:
    if not campaign_id:
        return []
    return [{"terms": {"campaign_id": [campaign_id, "__global__"]}}]


def _hit_to_result(hit: dict[str, Any]) -> dict[str, Any]:
    source = hit.get("_source", {})
    return {
        "document_id": source.get("document_id"),
        "chunk_id": source.get("chunk_id"),
        "retrieved_text": source.get("chunk_text", ""),
        "score": hit.get("_score"),
        "metadata": source.get("metadata") or {},
    }
