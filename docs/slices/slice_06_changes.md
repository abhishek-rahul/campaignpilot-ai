# Slice 06 Changes - Observability + Evaluation + Debug Dashboard

## Summary

Slice 6 adds read-only observability endpoints and deterministic advisory evaluation. The app can now inspect LLM traces, tool calls, debug timeline events, summary counts, and saved evaluation results without changing campaign generation, approval, payload, or delivery behavior.

## User-Visible Features

- Observability summary panel with counts for traces, RAG contexts, compliance, tools, payloads, delivery logs, refinements, and evaluations.
- LLM trace preview panel showing operation, mock/model, status, latency, prompt preview, and response preview.
- Tool call preview panel for compliance rule execution logs.
- Debug timeline panel combining chat, LLM, RAG, compliance, tools, payloads, delivery, refinements, and evaluations.
- Variant evaluation panel with deterministic score, grade, pass/fail, checks, and recommendation.
- Evaluation history panel.

## Backend Changes

- Added campaign observability endpoints for summary, LLM traces, tool calls, timeline, evaluations, and readiness evaluation.
- Added detail endpoints for LLM traces, tool calls, and evaluations.
- Added variant evaluation endpoint.
- Added `observability_service.py` and `observability_repository.py` for read-only aggregation and timeline mapping.
- Implemented deterministic evaluation in `evaluation_service.py`, `evaluation/variant_quality.py`, and `evaluation/scoring.py`.

## Frontend Changes

- Added `observabilityApi.ts` and `evaluationApi.ts`.
- Added observability and evaluation TypeScript types.
- Added summary, trace, tool-call, timeline, variant evaluation, and evaluation history panels.
- Extended `CampaignChatPage.tsx` without adding new routes/navigation.

## DB/Migration Changes

- Added migration `006_slice_6_observability_evaluation.py`.
- Added table `evaluation_results`.
- Intentionally did not add `evaluation_runs`; Slice 6 stores individual deterministic results only.

## API Contract Implemented

- All Slice 6 endpoints return the standard ApiResponse envelope.
- No new streaming endpoint was added.

## Evaluation Rules

Variant quality score totals 100:

- CTA presence: 20
- Channel length fit: 20
- Tone alignment: 15
- Offer present: 20
- Not too aggressive: 15
- Compliance-safe hints: 10

Grades: A >= 85, B >= 70, C >= 50, D < 50. Evaluation is advisory only and does not approve, reject, mutate, or send.

## Testing Evidence

Backend local verification:

```bash
cd backend
.venv/Scripts/python.exe -m compileall app
.venv/Scripts/python.exe -m pytest --basetemp C:/Users/bleas/AppData/Local/Temp/campaignpilot-pytest
```

Result: compile passed. Pytest collected 64 tests; 51 passed and 13 DB-backed integration tests were skipped in the host environment.

Docker-backed verification:

```bash
docker compose up -d --build
docker compose exec -T backend uv sync --extra dev
docker compose exec -T backend uv run alembic upgrade head
docker compose exec -T backend uv run python -m compileall app
docker compose exec -T backend uv run python -m pytest --basetemp /tmp/campaignpilot-pytest
```

Result: migration upgraded through `006_slice_6`; compile passed; pytest collected 64 tests and all 64 passed.

Frontend verification:

```bash
cd frontend
npm install
npm run build
```

Result: npm install was up to date and Vite build passed.

Docker smoke:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

Result: backend health returned a success envelope and Elasticsearch returned cluster metadata for version `8.19.0`.

## Known Limitations

- Debug dashboard is embedded in the existing page, not a separate dashboard route.
- Evaluation is deterministic and simple; it is not an LLM judge or legal/compliance system.
- Timeline is compact and does not expose full prompt/response bodies.

## Next Slice Handoff Notes

- Slice 7 can build richer analytics or auth if needed.
- Existing observability records are now exposed through stable read APIs.
