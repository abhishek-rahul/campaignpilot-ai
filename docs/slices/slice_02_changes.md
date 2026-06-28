# Slice 02 Changes - Brand/Product Document RAG

## Summary

Slice 2 adds document upload, text/PDF ingestion, chunking, mock or OpenAI embeddings, Elasticsearch indexing, retrieved context preview, campaign plan generation, and optional RAG-aware variant generation.

Slice 1 campaign chat and no-RAG variant generation remain backward compatible.

## User-Visible Features

- Upload `.txt`, `.md`, or `.pdf` documents after a campaign is created.
- Ingest uploaded documents into chunks and embeddings.
- View document status, error message, chunk count, and embedding count.
- Refresh retrieved context for a campaign.
- Generate a simple campaign plan from the campaign brief plus retrieved context.
- Generate variants with or without RAG context.

## Backend Changes

- Implemented `POST /api/v1/documents/upload`.
- Implemented `GET /api/v1/documents`.
- Implemented `GET /api/v1/documents/{document_id}`.
- Implemented `POST /api/v1/documents/{document_id}/ingest`.
- Implemented `GET /api/v1/campaigns/{campaign_id}/retrieved-context`.
- Implemented `POST /api/v1/campaigns/{campaign_id}/plan`.
- Extended `POST /api/v1/campaigns/{campaign_id}/generate-variants` to honor `use_rag_context=true`.
- Added safe custom error details while preserving uniform response envelopes.

## Frontend Changes

- Added document upload and document list panels to `CampaignChatPage`.
- Added ingest action per uploaded document.
- Added retrieved context preview.
- Added campaign plan panel.
- Added separate "Generate Variants with RAG" action while keeping the original no-RAG button.
- Added shared document/RAG API functions and TypeScript types.

## DB/Migration Changes

Migration added:

- `backend/alembic/versions/002_slice_2_document_rag.py`

Tables introduced:

- `brand_documents`
- `document_chunks`
- `embedding_records`
- `retrieved_contexts`

No Slice 3+ tables were added.

## API Contract Implemented

All new non-streaming endpoints return the existing envelope:

```json
{
  "success": true,
  "message": "Human readable message",
  "data": {},
  "error": null,
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "2026-06-28T00:00:00Z"
  }
}
```

Errors also use the standard envelope with `success=false`, `data=null`, and a safe error code.

## GenAI/RAG Components Implemented

- Deterministic text splitter.
- Text/Markdown/PDF document loader.
- OpenAI embedding wrapper behind `app/rag/embedding_client.py`.
- Mandatory mock embeddings when `OPENAI_API_KEY` is missing, empty, or `replace_me`.
- Elasticsearch vector store wrapper with lexical fallback during retrieval.
- RAG query builder from campaign brief fields.
- Retrieved context persistence.
- Mock campaign plan generation through the LLM wrapper.

## Testing Evidence

- Host `uv sync --extra dev` could not run because `uv` is not installed or not on PATH in this shell.
- Docker build succeeded and ran `uv sync --no-dev` inside the backend image.
- `.venv\Scripts\python.exe -m alembic upgrade head` passed after Docker Postgres started.
- `.venv\Scripts\python.exe -m compileall app` passed.
- `.venv\Scripts\python.exe -m pytest` passed: 18 passed.
- `npm install` passed.
- `npm run build` passed.
- `docker compose up -d --build` passed after Docker daemon access was approved.
- `curl.exe http://localhost:8000/api/v1/health` returned the standard successful health envelope.
- `curl.exe http://localhost:9200` returned Elasticsearch 8.19.0 cluster info after ES finished starting.

## Known Limitations

- DOCX, OCR, images, tables, approvals, compliance checks, delivery, memory, evaluation, and observability dashboards are intentionally not implemented.
- If Elasticsearch is unavailable during ingestion, chunks and embeddings metadata are saved and the document can still be used by lexical DB fallback, but ES document ids will be empty and an indexing warning is stored.
- Mock embeddings are deterministic but not semantically equivalent to real embeddings.
- Campaign plans are returned directly and are not persisted in a `campaign_plans` table.

## Next Slice Handoff Notes

- Slice 3 can build on `retrieved_contexts` and `message_variants` for compliance checks.
- A later hardening pass can add richer ES query strategy, persistent campaign plan tables, and stricter ingestion failure policy if needed.
