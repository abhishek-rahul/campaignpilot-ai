# Slice 04 Testing

## Setup Commands

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run python -m compileall app
uv run python -m pytest
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

Docker smoke:

```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

## Telegram Environment

Set these only when testing a real Telegram send:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Keep them as `replace_me` to verify the safe missing-credentials path.

## Full Manual API Flow

Create campaign:

```bash
curl -X POST http://localhost:8000/api/v1/chat/campaign \
  -H "Content-Type: application/json" \
  -d "{\"campaign_id\":null,\"message\":\"Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June.\",\"stream\":false}"
```

Generate variants:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/camp_xxx/generate-variants \
  -H "Content-Type: application/json" \
  -d "{\"variant_count\":3,\"channels\":[\"telegram\",\"whatsapp_mock\"],\"use_rag_context\":false,\"use_memory\":false}"
```

Run compliance:

```bash
curl -X POST http://localhost:8000/api/v1/variants/var_xxx/compliance-check \
  -H "Content-Type: application/json" \
  -d "{\"use_rag_context\":false}"
```

Approve variant:

```bash
curl -X POST http://localhost:8000/api/v1/variants/var_xxx/approve \
  -H "Content-Type: application/json" \
  -d "{\"reason\":\"Looks good\",\"allow_high_risk_override\":false}"
```

Check payload readiness:

```bash
curl http://localhost:8000/api/v1/campaigns/camp_xxx/payload-readiness
```

Generate payloads:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/camp_xxx/payloads \
  -H "Content-Type: application/json" \
  -d "{\"channels\":[\"telegram\",\"whatsapp_mock\"],\"regenerate\":false}"
```

List payloads:

```bash
curl http://localhost:8000/api/v1/campaigns/camp_xxx/payloads
```

Get payload detail:

```bash
curl http://localhost:8000/api/v1/payloads/payload_xxx
```

Send Telegram payload:

```bash
curl -X POST http://localhost:8000/api/v1/payloads/payload_telegram_xxx/send
```

List delivery logs:

```bash
curl http://localhost:8000/api/v1/campaigns/camp_xxx/delivery-logs
```

Get delivery detail:

```bash
curl http://localhost:8000/api/v1/delivery-logs/del_xxx
```

List channels:

```bash
curl http://localhost:8000/api/v1/channels
```

## Negative Tests

Generate payloads before approval:

Expected error code: `CAMPAIGN_NOT_APPROVED`.

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/camp_xxx/payloads \
  -H "Content-Type: application/json" \
  -d "{\"channels\":[\"telegram\"],\"regenerate\":false}"
```

Unsupported channel:

Expected error code: `UNSUPPORTED_CHANNEL`.

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/camp_xxx/payloads \
  -H "Content-Type: application/json" \
  -d "{\"channels\":[\"email\"],\"regenerate\":false}"
```

Send WhatsApp mock payload:

Expected error code: `CHANNEL_SEND_NOT_SUPPORTED`.

```bash
curl -X POST http://localhost:8000/api/v1/payloads/payload_whatsapp_xxx/send
```

Send Telegram without credentials:

Expected error code: `TELEGRAM_CREDENTIALS_MISSING`.

## Manual Frontend Steps

1. Open frontend.
2. Submit the campaign prompt.
3. Generate variants.
4. Run compliance on one variant.
5. Approve the variant.
6. Confirm payload readiness becomes ready.
7. Click Generate Channel Payloads.
8. Confirm Telegram and WhatsApp mock previews render.
9. Click Send Telegram.
10. If credentials are missing, confirm the error is clear.
11. If credentials are configured, confirm delivery log status is `SENT`.

## Verify DB Rows

```sql
select id, campaign_id, variant_id, channel, payload_type, status, created_at
from channel_payloads
order by created_at desc;

select id, campaign_id, payload_id, channel, status, provider_message_id, error_message, sent_at
from delivery_logs
order by created_at desc;
```

## Troubleshooting

- `CAMPAIGN_NOT_APPROVED`: approve a compliant variant first.
- `SELECTED_VARIANT_REQUIRED`: approval did not set `campaigns.selected_variant_id`.
- `SELECTED_VARIANT_NOT_APPROVED`: selected variant is not approved.
- `UNSUPPORTED_CHANNEL`: Slice 4 supports only `telegram` and `whatsapp_mock`.
- `TELEGRAM_CREDENTIALS_MISSING`: set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- `CHANNEL_SEND_NOT_SUPPORTED`: WhatsApp mock cannot be sent in Slice 4.
