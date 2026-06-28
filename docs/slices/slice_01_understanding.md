# Slice 01 Understanding - Campaign Chat + Brief + Variants

## What Slice 1 Does

Slice 1 turns a campaign idea into a saved campaign workflow:

1. The user enters a campaign idea in the frontend.
2. The frontend sends `campaign_id: null` for the first message.
3. The backend creates a campaign if no `campaign_id` exists.
4. The LLM layer extracts a structured brief.
5. The backend saves campaign, brief, user message, AI reply, and LLM trace.
6. The user generates variants from the saved brief.
7. The backend saves message variants and returns them to the frontend.

## End-to-End Flow

The frontend calls `POST /api/v1/chat/campaign` with a message. For the first message, `campaign_id` is `null`; that is the signal for the backend to create the campaign automatically. The backend validates the message, creates or loads the campaign, calls the LLM wrapper, saves the extracted brief, saves conversation messages, records an LLM trace, and returns the extracted brief plus AI reply.

After the first response, the UI keeps the returned `campaign_id`. Further chat submissions use that same campaign ID, so the conversation grows under one campaign instead of creating a new one each time.

When the user clicks Generate Variants, the frontend calls `POST /api/v1/campaigns/{campaign_id}/generate-variants`. The backend loads the saved brief, uses only that brief to generate variants, saves them, marks the campaign as `VARIANTS_GENERATED`, and returns the cards.

## Backend Responsibilities

- Routes convert HTTP requests into service calls and wrap responses with the existing API envelope.
- Services own workflow decisions such as creating campaigns, checking brief completeness, and updating statuses.
- Repositories isolate SQLAlchemy persistence.
- Models define only Slice 1 tables.
- The LLM wrapper is the only backend layer that can call OpenAI.
- Trace service records successful and failed LLM operations.

## Frontend Responsibilities

- `CampaignChatPage` owns the Slice 1 user flow.
- There is no separate Create Campaign button in the main UI; campaign creation happens through chat.
- Chat API sends campaign messages.
- Variant API generates and lists variants.
- Brief preview component displays extracted structured fields.
- Variant card grid displays generated messages.

## DB Tables Introduced

- `campaign_managers`: local owner for campaigns while auth is not implemented.
- `campaigns`: central workflow record and status.
- `campaign_briefs`: structured brief extracted from chat.
- `conversation_messages`: user and AI chat history.
- `message_variants`: generated campaign message options.
- `llm_traces`: prompt/response metadata for brief extraction and variant generation.

## How Chat Creates Campaign And Brief

If `campaign_id` is null, the chat service creates a draft campaign. It then saves the user message, extracts the brief, upserts `campaign_briefs`, saves the AI reply, and records an LLM trace. If all required fields exist, the brief is marked `COMPLETE` and campaign status becomes `BRIEF_EXTRACTED`.

If `campaign_id` is provided, the service loads that existing campaign and saves the new user and AI messages against it. This gives a basic continuing chat history.

Important limitation: Slice 1 does not yet provide true conversational memory. The LLM extraction mainly works from the latest message, so short follow-up commands may not merge perfectly with the previous brief. Full memory/refinement belongs to a later slice.

## How Variant Generation Works

Variant generation requires an existing campaign and a complete brief. It does not use RAG, Elasticsearch, memory, compliance, approvals, channels, or delivery. It calls the LLM wrapper with campaign brief fields and saves 3 to 5 `message_variants`.

## LLM Wrapper And Mock Fallback

`backend/app/llm/llm_client.py` decides whether to call OpenAI or mock mode. Mock mode is mandatory when `OPENAI_API_KEY` is missing, empty, or `replace_me`. This keeps local development and tests usable without paid API calls.

## Frontend To Backend Communication

Frontend API helpers use the shared response handler. Endpoint-specific fields are read from `response.data`, matching the v3 API contract.

## Important Design Decisions

- `campaigns.selected_variant_id` is nullable text in Slice 1, not an FK, to avoid migration circularity.
- PostgreSQL/Alembic is the source of truth for DB schema.
- `campaign_id` is a JSON string in API requests, so existing campaign IDs must be sent as `"camp_xxx"`, not bare `camp_xxx`.
- Future-slice routers remain registered but their endpoints stay placeholders.
- OpenAI/LangChain are not imported in routes or business services.

## Intentionally Not Implemented Yet

RAG, document ingestion, embeddings, Elasticsearch retrieval, compliance, approval, channels, delivery, Telegram sending, WhatsApp mock payloads, streaming, memory, evaluation, observability dashboards, and production auth are outside Slice 1.
