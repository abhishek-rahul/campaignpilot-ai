# Slice 04 Changes - Channel Payloads + Telegram Send

## Summary

Slice 4 adds approved-variant channel payload generation, WhatsApp mock payload preview, explicit Telegram send, and delivery log persistence. Payload generation is blocked until a campaign is `APPROVED` and has an approved `selected_variant_id`.

## User-Visible Features

- See whether payload generation is ready and why it may be blocked.
- Generate Telegram and WhatsApp mock payloads from the approved selected variant.
- Preview generated payload text and JSON.
- Send only Telegram payloads by explicit user action.
- View delivery/send attempt logs.

## Backend Changes

- Implemented payload readiness, payload generation, payload listing, payload detail, Telegram send, delivery listing, delivery detail, and channel list endpoints.
- Added channel adapter registry with Telegram and WhatsApp mock adapters.
- Added Telegram Bot API send behind the Telegram adapter only.
- Added validation that campaign and selected variant are approved before payload generation or send.
- WhatsApp remains mock-only and cannot be sent.

## Frontend Changes

- Added payload readiness panel.
- Added payload generation controls with channel checkboxes and regenerate option.
- Added payload preview cards.
- Added Send Telegram action for Telegram payloads only.
- Added delivery log display.

## DB / Migration Changes

Migration added:

- `backend/alembic/versions/004_slice_4_channels_delivery.py`

Tables introduced:

- `channel_payloads`
- `delivery_logs`

No `channels`, `recipients`, scheduler, retry, webhook, memory, or evaluation tables were added in Slice 4.

## API Contract Implemented

All new endpoints use the standard `success`, `message`, `data`, `error`, `meta` envelope.

Implemented:

- `GET /api/v1/channels`
- `GET /api/v1/campaigns/{campaign_id}/payload-readiness`
- `POST /api/v1/campaigns/{campaign_id}/payloads`
- `GET /api/v1/campaigns/{campaign_id}/payloads`
- `GET /api/v1/payloads/{payload_id}`
- `POST /api/v1/payloads/{payload_id}/send`
- `GET /api/v1/campaigns/{campaign_id}/delivery-logs`
- `GET /api/v1/delivery-logs/{delivery_id}`

## Channel Adapter Components

- `backend/app/channels/base_channel.py`: adapter interface and payload/send result DTOs.
- `backend/app/channels/channel_registry.py`: supported channel registry.
- Telegram adapter: payload generation and real Telegram Bot API send.
- WhatsApp mock adapter: payload generation only.

## Payload Generation Flow

1. Load campaign.
2. Require `campaign.status == APPROVED`.
3. Require `campaign.selected_variant_id`.
4. Load selected variant.
5. Require selected variant status `APPROVED`.
6. Build payloads through channel registry adapters.
7. Save rows in `channel_payloads`.
8. Return generated or existing payloads.

## Telegram Details

- Telegram payload uses approved variant `message_body`.
- CTA link is appended if present in the brief and missing from the message.
- Telegram send requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- Missing credentials return `TELEGRAM_CREDENTIALS_MISSING`.
- Provider send failures persist a `FAILED` delivery row and return `TELEGRAM_SEND_FAILED`.

## WhatsApp Mock Details

- WhatsApp payload includes provider-neutral mock fields.
- No Meta API call is made.
- Sending a WhatsApp mock payload returns `CHANNEL_SEND_NOT_SUPPORTED`.

## Delivery Logs

- Every successful Telegram send creates a `SENT` delivery log.
- Telegram provider failures create a `FAILED` delivery log.
- Logs represent explicit user-triggered sends only.

## Testing Evidence

Backend compile:

```bash
cd backend
.\.venv\Scripts\python.exe -m compileall app
```

Result: passed.

Focused backend unit tests:

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest tests\unit\test_channel_payload_adapters.py tests\unit\test_telegram_adapter.py tests\unit\test_payload_service.py tests\unit\test_delivery_service.py --basetemp %TEMP%\campaignpilot-pytest-slice4-unit
```

Result: `12 passed, 1 warning`.

Full backend tests:

```powershell
$env:DATABASE_URL='postgresql+psycopg://campaignpilot:campaignpilot@localhost:5432/campaignpilot'
$env:OPENAI_API_KEY='replace_me'
.\.venv\Scripts\python.exe -m pytest --basetemp %TEMP%\campaignpilot-pytest-slice4
```

Result: `47 passed, 1 warning`.

Frontend build:

```bash
cd frontend
npm install
npm run build
```

Result: passed.

Docker-backed migration and smoke:

```bash
docker compose up -d --build
docker compose exec backend uv run alembic upgrade head
docker compose exec backend uv run python -m compileall app
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

Result: passed. Alembic ran `003_slice_3 -> 004_slice_4`.

Host limitation: direct `uv sync --extra dev` could not run because `uv` is not installed or not on PATH in this Windows shell. Docker backend build successfully ran `uv sync --no-dev`, and Docker `uv run alembic upgrade head` succeeded.

## Known Limitations

- Real WhatsApp sending is intentionally not implemented.
- Telegram send is single explicit API/UI action; no retry worker or scheduler.
- No recipient management in Slice 4.
- Telegram credentials are environment-only and are not required for automated tests.

## Next Slice Handoff

Slice 5 can build streaming/refinement/memory on top of the approved campaign and payload state. Slice 6 can expose richer delivery/tool observability.
