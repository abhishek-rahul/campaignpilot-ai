# Slice 05 Testing - Streaming Chat + Refinement Loop

## Setup

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
```

If `uv` is not available on the host, run the same commands inside the backend container or use the existing virtual environment only for local compile/test checks.

## Backend Commands

```bash
cd backend
uv run python -m compileall app
uv run python -m pytest
```

On Windows, if pytest cache permissions fail, use a temp folder outside the repo:

```bash
uv run python -m pytest --basetemp C:/Users/bleas/AppData/Local/Temp/campaignpilot-pytest
```

## Frontend Commands

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

## Manual API Flow

### 1. Streaming Chat

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/campaign/stream \
  -H "Content-Type: application/json" \
  -d "{\"campaign_id\":null,\"message\":\"Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June.\",\"stream\":true}"
```

Expected SSE events:

```text
event: start
event: token
event: brief_delta
event: final
```

Save `campaign_id` from the final event.

### 2. Refine Brief Without Applying

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/refine-brief \
  -H "Content-Type: application/json" \
  -d "{\"feedback\":\"Make the tone premium and less pushy\",\"use_rag_context\":false,\"apply\":false}"
```

Expected: normal ApiResponse envelope with `applied:false`.

### 3. Apply Brief Refinement

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/refine-brief \
  -H "Content-Type: application/json" \
  -d "{\"feedback\":\"Make the tone premium and less pushy\",\"use_rag_context\":false,\"apply\":true}"
```

Expected: `after_brief.tone` changes to `premium`. If the campaign was already approved, `campaign_status` becomes `NEEDS_REVIEW` and `selected_variant_id` becomes null.

### 4. Generate Variants

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/generate-variants \
  -H "Content-Type: application/json" \
  -d "{\"variant_count\":3,\"channels\":[\"telegram\"],\"use_rag_context\":false}"
```

Save one `variant_id`.

### 5. Refine Variant

```bash
curl -X POST http://localhost:8000/api/v1/variants/VARIANT_ID/refine \
  -H "Content-Type: application/json" \
  -d "{\"feedback\":\"Make it shorter and softer\",\"use_rag_context\":false,\"create_new_variant\":true}"
```

Expected: response includes a new `refined_variant` with status `GENERATED`.

### 6. Regenerate Variants From Feedback

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/regenerate-variants \
  -H "Content-Type: application/json" \
  -d "{\"feedback\":\"Make all variants softer\",\"variant_count\":3,\"channels\":[\"telegram\"],\"use_rag_context\":false}"
```

Expected: 3 new generated variants.

### 7. List Refinement History

```bash
curl http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/refinements
```

Expected: history rows for brief refinement, variant refinement, and variant regeneration.

## Manual Frontend Testing

1. Start backend and frontend.
2. Open the Campaign Chat page.
3. Enter the manual campaign prompt.
4. Click `Send with Streaming`.
5. Confirm the streaming panel fills with tokens and final chat history appears.
6. Confirm brief preview is complete.
7. Use Brief Refinement with feedback like `Make the tone premium and less pushy`.
8. Confirm brief tone updates and refinement history shows a row.
9. Generate variants.
10. Select a variant in Variant Refinement and submit `Make it shorter`.
11. Confirm a new generated variant appears.
12. Use Regenerate Variants from Feedback.
13. Confirm additional variants and refinement history rows appear.

## DB Verification

```sql
select id, campaign_id, refinement_type, source_type, status, created_at
from campaign_refinements
order by created_at desc;

select id, operation_name, used_mock, created_at
from llm_traces
where operation_name in (
  'streaming_brief_extraction',
  'brief_refinement',
  'variant_refinement',
  'variant_regeneration'
)
order by created_at desc;
```

## Troubleshooting

- If `ModuleNotFoundError: No module named 'app'` appears, run pytest from `backend`, not the repo root.
- If DB-backed integration tests skip, run `uv run alembic upgrade head` and confirm Postgres is reachable.
- If streaming shows only an error event, inspect backend logs and confirm `OPENAI_API_KEY=replace_me` for mock fallback or a real key for provider mode.
- If payload generation is blocked after brief refinement, that is expected after safe reset; regenerate variants, rerun compliance, approve, then generate payloads again.

## Current Local Evidence

- `docker compose exec -T backend uv run alembic upgrade head` passed and applied Slice 5 migration.
- `docker compose exec -T backend uv run python -m compileall app` passed.
- `docker compose exec -T backend uv run python -m pytest --basetemp /tmp/campaignpilot-pytest` passed: 56 tests.
- `cd frontend && npm install` passed.
- `cd frontend && npm run build` passed.
- `curl http://localhost:8000/api/v1/health` passed.
- `curl http://localhost:9200` passed after Elasticsearch completed startup.
