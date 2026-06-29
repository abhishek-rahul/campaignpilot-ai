# Slice 04 Understanding

## What Slice 4 Does

Slice 4 turns an approved campaign variant into channel-ready payloads and lets the user explicitly send the Telegram payload.

The flow is:

1. Create campaign from chat.
2. Generate variants.
3. Run compliance.
4. Approve one variant.
5. Generate channel payloads.
6. Preview Telegram and WhatsApp mock payloads.
7. Send Telegram.
8. Store delivery logs.

## Backend Responsibilities

- `campaign_routes.py`: campaign-owned payload readiness, payload generation, payload list, and delivery log list endpoints.
- `delivery_routes.py`: payload detail, send payload, and delivery detail endpoints.
- `channel_routes.py`: supported channel capability list.
- `channel_service.py`: readiness checks and payload generation workflow.
- `delivery_service.py`: Telegram send validation and delivery log persistence.
- `channels/`: provider-specific adapter logic.

## Frontend Responsibilities

- `CampaignChatPage.tsx`: keeps the Slice 1-4 workflow on one MVP screen.
- `PayloadReadinessPanel`: explains whether payloads can be generated.
- `PayloadGenerationPanel`: lets the user choose channels and generate payloads.
- `PayloadPreviewPanel`: displays channel payload JSON and Telegram send action.
- `DeliveryLogPanel`: displays send attempts.

## DB Tables Introduced

- `channel_payloads`: saved Telegram and WhatsApp mock payloads.
- `delivery_logs`: explicit Telegram send attempts and provider results.

## Payload Readiness

Payload generation is ready only when:

- campaign exists
- campaign status is `APPROVED`
- `selected_variant_id` exists
- selected variant belongs to the campaign
- selected variant status is `APPROVED`

## Channel Adapters

The backend uses a registry so services do not know provider details directly.

- Telegram adapter supports payload generation and send.
- WhatsApp mock adapter supports payload generation only.

## Telegram Payload And Send

Telegram payload text comes from the approved selected variant. If the campaign brief has a CTA link and the text does not contain it, the adapter appends it.

Telegram send uses:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

The send call goes through the Telegram adapter, not routes or campaign service.

## WhatsApp Mock Payload

WhatsApp mock payload is a preview/debug artifact only. It is provider-neutral and does not call Meta APIs.

## Important Design Decisions

- `regenerate=false` returns existing generated payloads when all requested channels already exist.
- `regenerate=true` creates a new payload row set and preserves older rows.
- Missing Telegram credentials return a safe validation error.
- Telegram provider failures are persisted as failed delivery logs.

## Intentionally Not Implemented

Slice 4 does not implement real WhatsApp sending, recipients, scheduling, retries, webhooks, streaming, memory, evaluation dashboards, MCP, production auth, or auto-send.
