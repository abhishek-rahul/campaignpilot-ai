# Slice 02 Testing

## Backend Setup

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run python -m compileall app
uv run python -m pytest
```

Run Alembic before DB-backed API tests because Slice 2 adds `brand_documents`, `document_chunks`, `embedding_records`, and `retrieved_contexts`.

## Frontend Build

```bash
cd frontend
npm install
npm run build
```

## Docker Smoke Test

```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

## Curl Examples

Create a campaign:

```bash
curl -X POST http://localhost:8000/api/v1/chat/campaign \
  -H "Content-Type: application/json" \
  -d "{\"campaign_id\":null,\"message\":\"Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June.\",\"stream\":false}"
```

Upload a text document:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "document_type=brand_guideline" \
  -F "campaign_id=camp_your_id" \
  -F "file=@brand_guidelines.txt;type=text/plain"
```

List documents:

```bash
curl "http://localhost:8000/api/v1/documents?campaign_id=camp_your_id"
```

Get one document:

```bash
curl http://localhost:8000/api/v1/documents/doc_your_id
```

Expected `data` fields:

```json
{
  "document_id": "doc_xxx",
  "original_filename": "brand_guidelines.txt",
  "document_type": "brand_guideline",
  "status": "INGESTED",
  "file_size_bytes": 1234,
  "content_type": "text/plain",
  "error_message": null,
  "chunks_count": 2,
  "embeddings_count": 2,
  "created_at": "2026-06-28T00:00:00Z",
  "ingested_at": "2026-06-28T00:00:00Z"
}
```

Ingest document:

```bash
curl -X POST http://localhost:8000/api/v1/documents/doc_your_id/ingest \
  -H "Content-Type: application/json" \
  -d "{\"chunk_size\":1000,\"chunk_overlap\":150}"
```

Refresh retrieved context:

```bash
curl "http://localhost:8000/api/v1/campaigns/camp_your_id/retrieved-context?refresh=true&top_k=5"
```

Generate campaign plan:

```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/camp_your_id/plan?top_k=5"
```

Generate variants without RAG:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/camp_your_id/generate-variants \
  -H "Content-Type: application/json" \
  -d "{\"variant_count\":3,\"use_rag_context\":false,\"use_memory\":false}"
```

Generate variants with RAG:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/camp_your_id/generate-variants \
  -H "Content-Type: application/json" \
  -d "{\"variant_count\":3,\"use_rag_context\":true,\"use_memory\":false}"
```

Unsupported file error:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "document_type=brand_guideline" \
  -F "file=@brand.docx"
```

Expected error code: `UNSUPPORTED_FILE_TYPE`.

## Manual Frontend Steps

1. Open the frontend.
2. Submit the Slice 1 manual campaign prompt.
3. Confirm chat history and brief preview are visible.
4. Upload a `.txt` or `.md` brand guideline.
5. Click `Ingest`.
6. Confirm document status and chunk/embedding counts update.
7. Click `Refresh` in retrieved context.
8. Click `Generate Plan`.
9. Click `Generate Variants with RAG`.
10. Confirm variant cards render.

## Verify DB Rows

```sql
select id, original_filename, status, error_message, ingested_at
from brand_documents
order by created_at desc;

select document_id, count(*)
from document_chunks
group by document_id;

select document_id, status, count(*)
from embedding_records
group by document_id, status;

select campaign_id, used_for, count(*)
from retrieved_contexts
group by campaign_id, used_for;
```

## Verify LLMTrace Rows

```sql
select campaign_id, operation_name, model_name, status, metadata
from llm_traces
where operation_name in ('campaign_plan_generation', 'variant_generation')
order by created_at desc;
```

## Troubleshooting

- If backend tests skip integration tests, start Postgres and run `uv run alembic upgrade head`.
- If OpenAI keys are missing, mock LLM and mock embeddings should still work.
- If Elasticsearch is down during ingestion, document rows may still show `INGESTED` with an indexing warning in `error_message`; retrieval can use DB lexical fallback.
- If file upload fails with `UNSUPPORTED_FILE_TYPE`, use `.txt`, `.md`, or `.pdf`.
