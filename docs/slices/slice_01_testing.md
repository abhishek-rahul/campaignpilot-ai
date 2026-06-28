# Slice 01 Testing Guide

## Setup

Create backend environment file if needed:

```bash
cp .env.example backend/.env
```

For mock LLM mode, keep:

```env
OPENAI_API_KEY=replace_me
```

## Backend Commands

Run dependency sync, migration, compile, and tests:

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run python -m compileall app
uv run python -m pytest
```

The Alembic upgrade must run before DB-backed API tests.

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

## Manual Test Prompt

```text
Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June.
```

## Curl Examples

Health:

```bash
curl http://localhost:8000/api/v1/health
```

Chat campaign:

Git Bash recommended form:

```bash
curl -X POST http://localhost:8000/api/v1/chat/campaign \
  -H "Content-Type: application/json" \
  -d '{"campaign_id":null,"message":"Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June.","stream":false}'
```

PowerShell or escaped double-quote form:

```bash
curl -X POST http://localhost:8000/api/v1/chat/campaign \
  -H "Content-Type: application/json" \
  -d "{\"campaign_id\":null,\"message\":\"Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June.\",\"stream\":false}"
```

Continue an existing campaign chat:

```bash
curl -X POST http://localhost:8000/api/v1/chat/campaign \
  -H "Content-Type: application/json" \
  -d '{"campaign_id":"camp_xxx","message":"Make the tone more professional.","stream":false}'
```

`campaign_id` must be quoted because it is a JSON string. Bare `camp_xxx` causes a JSON decode error.

Create campaign directly:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Content-Type: application/json" \
  -d "{\"campaign_name\":\"Direct Campaign\",\"goal\":\"Reactivate customers\",\"target_audience\":\"inactive customers\",\"offer_details\":\"25% discount\",\"tone\":\"friendly\",\"preferred_channels\":[\"telegram\"],\"cta_link\":\"https://example.com/sale\",\"expiry_date\":\"2026-06-30\"}"
```

List campaigns:

```bash
curl http://localhost:8000/api/v1/campaigns
```

Get campaign:

```bash
curl http://localhost:8000/api/v1/campaigns/camp_xxx
```

Update campaign:

```bash
curl -X PATCH http://localhost:8000/api/v1/campaigns/camp_xxx \
  -H "Content-Type: application/json" \
  -d "{\"tone\":\"professional\"}"
```

Get conversation:

```bash
curl http://localhost:8000/api/v1/campaigns/camp_xxx/conversation
```

Generate variants:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/camp_xxx/generate-variants \
  -H "Content-Type: application/json" \
  -d "{\"variant_count\":3,\"channels\":[\"telegram\",\"whatsapp_mock\"],\"use_rag_context\":false,\"use_memory\":false}"
```

List variants:

```bash
curl http://localhost:8000/api/v1/campaigns/camp_xxx/variants
```

Update variant:

```bash
curl -X PATCH http://localhost:8000/api/v1/variants/var_xxx \
  -H "Content-Type: application/json" \
  -d "{\"message_body\":\"Updated short message body\",\"tone\":\"friendly\"}"
```

## Expected Response Shape

Success:

```json
{
  "success": true,
  "message": "Human readable message",
  "data": {},
  "error": null,
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "2026-06-24T18:30:00Z"
  }
}
```

Error:

```json
{
  "success": false,
  "message": "Human readable error",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "details": []
  },
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "2026-06-24T18:30:00Z"
  }
}
```

## Manual Frontend Testing

1. Start backend after migrations.
2. Start frontend with `npm run dev`.
3. Open `http://localhost:5173`.
4. Paste or keep the manual test prompt in the Campaign idea box.
5. Click `Send to AI`.
6. Confirm a campaign ID appears on the page.
7. Confirm chat history shows user and AI messages.
8. Confirm brief preview is complete.
9. Click Generate Variants.
10. Confirm variant cards render.

There is no separate Create Campaign button in the Slice 1 UI. The first chat request sends `campaign_id: null`, and the backend creates the campaign automatically.

## Verify DB Rows

Use psql or a DB client:

```sql
select id, campaign_name, status from campaigns order by created_at desc;
select campaign_id, brief_status, missing_fields from campaign_briefs order by created_at desc;
select campaign_id, sender, message_text from conversation_messages order by created_at desc;
select campaign_id, channel, status from message_variants order by created_at desc;
```

## Verify LLMTrace Rows

```sql
select campaign_id, operation_name, model_name, status, metadata
from llm_traces
order by created_at desc;
```

In mock mode, trace metadata should include `"used_mock": true`.

## Troubleshooting

- `uv` not found: install uv or add it to PATH.
- Missing tables: run `uv run alembic upgrade head`.
- Host-side DB connection fails with `getaddrinfo failed`: `backend/.env` may be using `postgres` as the host. That name works inside Docker; use `localhost` when running backend commands directly on the host.
- API key missing: this is okay for Slice 1; mock fallback should run.
- Real OpenAI errors: check `llm_traces` for failed trace rows.
- Variant generation returns brief incomplete: send a chat message with goal, audience, offer, tone, channel, CTA, and expiry.
- JSON decode error near `campaign_id`: quote existing IDs as `"camp_xxx"` or use `null` for a new campaign.
