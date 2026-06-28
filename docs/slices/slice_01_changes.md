# Slice 01 Changes - Campaign Chat + Brief Extraction + Variant Generation

## 1. Summary

Implemented the first vertical slice: campaign chat creates or updates a campaign, extracts a structured campaign brief through the LLM wrapper or deterministic mock fallback, saves conversation messages and LLM traces, and generates 3 to 5 message variants from the saved brief.

## 2. User-visible Features

- Campaign Chat page accepts a campaign idea.
- Extracted brief preview shows goal, audience, offer, tone, channels, CTA, expiry, status, and missing fields.
- Generate Variants button creates channel-aware variant cards.
- Variant cards show name, channel, message body, tone, reason, risk level, and status.

## 3. Backend Changes

- Implemented Slice 1 routes for chat, campaigns, conversations, variant generation, variant listing, and variant updates.
- Added safe API envelope exception handlers without changing FastAPI app startup, CORS, existing router registration, or health behavior.
- Added SQLAlchemy models and repositories for Slice 1 entities.
- Added campaign, chat, variant, and trace services.
- Added LLM prompt builder, structured JSON parsing, real OpenAI wrapper path, and mandatory mock fallback when `OPENAI_API_KEY` is missing, empty, or `replace_me`.

## 4. Frontend Changes

- Implemented `CampaignChatPage` as the Slice 1 working screen.
- Added typed API helpers for chat, campaigns, and variants.
- Added campaign, chat, and variant TypeScript types.
- Added small display components for chat history, brief preview, and variant cards.

## 5. DB / Migration Changes

- Added Alembic migration `001_slice_1_campaign_chat.py`.
- Introduced only Slice 1 tables:
  - `campaign_managers`
  - `campaigns`
  - `campaign_briefs`
  - `conversation_messages`
  - `message_variants`
  - `llm_traces`
- `campaigns.selected_variant_id` is a nullable string without FK in Slice 1 to avoid circular migration ordering.
- Added default local campaign manager seed row for the no-auth Slice 1 flow.

## 6. API Contract Implemented

Implemented the Slice 1 subset of the v3 API contract:

- `GET /api/v1/health`
- `POST /api/v1/chat/campaign`
- `POST /api/v1/campaigns`
- `GET /api/v1/campaigns`
- `GET /api/v1/campaigns/{campaign_id}`
- `PATCH /api/v1/campaigns/{campaign_id}`
- `GET /api/v1/campaigns/{campaign_id}/conversation`
- `POST /api/v1/campaigns/{campaign_id}/generate-variants`
- `GET /api/v1/campaigns/{campaign_id}/variants`
- `PATCH /api/v1/variants/{variant_id}`

All non-streaming responses use the uniform `success`, `message`, `data`, `error`, `meta` envelope.

## 7. GenAI Components Implemented

- Brief extraction prompt assembly.
- Variant generation prompt assembly.
- Structured JSON parser and normalizer.
- OpenAI chat wrapper behind `llm_client.py`.
- Deterministic mock LLM fallback for local/test usage.
- Basic LLM trace persistence for brief extraction and variant generation.

## 8. Testing Evidence

Commands run in this workspace:

```bash
cd backend
python -m compileall app
```

Result: passed.

```bash
cd frontend
npm run build
```

Result: passed.

`uv` was not available on this shell PATH, so the required uv commands could not be executed here. Plain `python -m pytest` could not collect tests in this shell because the global Python environment does not have FastAPI/OpenAI dependencies installed. Use the documented uv flow for the real backend test gate.

## 9. Known Limitations

- No auth yet; Slice 1 uses a default local campaign manager.
- Mock LLM is deterministic and intentionally simple.
- Real OpenAI JSON quality still depends on provider output, with parser validation around it.
- DB-backed API tests require Postgres and `uv run alembic upgrade head`.
- Future-slice routes remain placeholders.

## 10. Next Slice Handoff

Slice 2 should add document upload, ingestion, chunks, embeddings, Elasticsearch retrieval, and retrieved context tables without changing the Slice 1 campaign/chat/variant contract unless necessary.
