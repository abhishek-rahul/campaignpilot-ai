# Slice 03 Changes - Compliance Guardrails + Human Approval

## Summary

Slice 3 adds deterministic compliance guardrails and human approval/rejection for generated variants. It keeps Slice 1 chat/variant generation and Slice 2 RAG flows backward compatible.

## User-Visible Features

- Run compliance check on each generated variant.
- View compliance status, risk level, issues, and recommendation on variant cards.
- Approve variants that passed or have warnings.
- Reject variants with a reason.
- See campaign-level compliance summary counts.

## Backend Changes

- Implemented variant compliance check, compliance history, approve, and reject endpoints.
- Added campaign compliance summary endpoint.
- Added deterministic compliance rules for misleading claims, aggressive urgency, expiry clarity, CTA presence, offer consistency, excessive emoji, channel fit, and brand context awareness.
- Added internal tool-call logging for each rule execution.
- Added approval workflow that blocks failed variants unless explicit override is provided.

## Frontend Changes

- Added per-variant compliance panel.
- Added Run Compliance Check, Approve, and Reject controls.
- Added compact campaign compliance summary.
- Added Slice 3 API helpers and TypeScript types.

## DB / Migration Changes

Migration added:

- `backend/alembic/versions/003_slice_3_compliance_approval.py`

Tables introduced:

- `compliance_results`
- `approvals`
- `tool_call_logs`

No delivery, channel payload, scheduling, memory, evaluation, or observability dashboard tables were added.

## API Contract Implemented

All new non-streaming endpoints use the standard `success`, `message`, `data`, `error`, `meta` envelope.

Implemented:

- `POST /api/v1/variants/{variant_id}/compliance-check`
- `GET /api/v1/variants/{variant_id}/compliance-checks`
- `POST /api/v1/variants/{variant_id}/approve`
- `POST /api/v1/variants/{variant_id}/reject`
- `GET /api/v1/campaigns/{campaign_id}/compliance-summary`

## Compliance / Guardrail Components Implemented

- Deterministic rule functions in `backend/app/tools/compliance_rules.py`.
- Rule runner and aggregate scoring in `backend/app/tools/guardrail_runner.py`.
- Tool execution metadata saved to `tool_call_logs`.
- No external legal/compliance API is used.

## Approval Workflow Details

- Approval requires a latest compliance result.
- `PASSED` and `WARNING` can be approved.
- `FAILED` is blocked unless `allow_high_risk_override=true`.
- Approving sets variant status to `APPROVED`, sets `campaigns.selected_variant_id`, and updates campaign status to `APPROVED`.
- Rejecting sets variant status to `REJECTED` and stores an audit row.
- Approval does not send campaign or generate channel payloads.

## Testing Evidence

Local evidence:

```bash
cd backend
.\.venv\Scripts\python.exe -m compileall app
```

Passed.

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest --basetemp <Windows temp>\campaignpilot-pytest
```

Environment override used for host testing:

```powershell
$env:DATABASE_URL='postgresql+psycopg://campaignpilot:campaignpilot@localhost:5432/campaignpilot'
$env:OPENAI_API_KEY='replace_me'
```

Result: `32 passed, 1 warning`.

```bash
cd frontend
npm install
npm run build
```

Passed.

Docker-backed migration and smoke evidence:

```bash
docker compose up -d --build
docker compose exec backend uv run alembic upgrade head
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

Passed.

Host limitation: `uv sync --extra dev` could not be run directly on Windows because `uv` was not available on the host PATH. Docker backend build used `uv sync --no-dev`, and Docker `uv run alembic upgrade head` succeeded.

## Known Limitations

- Guardrails are deterministic MVP checks, not legal advice.
- No external compliance vendor integration.
- No LLM compliance judge is enabled in Slice 3.
- No Telegram/WhatsApp payload generation or sending.
- Tool call logs are persisted but not exposed through the Slice 6 observability endpoint yet.

## Next Slice Handoff

Slice 4 can require `campaign.status=APPROVED` and `campaigns.selected_variant_id` before generating channel payloads or sending Telegram messages.
