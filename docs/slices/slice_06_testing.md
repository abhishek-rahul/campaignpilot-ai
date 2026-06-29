# Slice 06 Testing - Observability + Evaluation

## Setup

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
```

## Backend Commands

```bash
cd backend
uv run python -m compileall app
uv run python -m pytest
```

## Frontend Commands

```bash
cd frontend
npm install
npm run build
```

## Docker Smoke

```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

## Latest Verification Evidence

Host backend:

```bash
cd backend
.venv/Scripts/python.exe -m compileall app
.venv/Scripts/python.exe -m pytest --basetemp C:/Users/bleas/AppData/Local/Temp/campaignpilot-pytest
```

Observed result: compile passed. Pytest collected 64 tests; 51 passed and 13 DB-backed integration tests were skipped because the host environment did not provide the full DB-backed runtime.

Docker backend:

```bash
docker compose up -d --build
docker compose exec -T backend uv sync --extra dev
docker compose exec -T backend uv run alembic upgrade head
docker compose exec -T backend uv run python -m compileall app
docker compose exec -T backend uv run python -m pytest --basetemp /tmp/campaignpilot-pytest
```

Observed result: Alembic upgraded through `006_slice_6`; compile passed; pytest collected 64 tests and all 64 passed.

Frontend:

```bash
cd frontend
npm install
npm run build
```

Observed result: dependencies were already up to date and build passed.

Smoke:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

Observed result: backend health returned the standard success envelope and Elasticsearch returned cluster metadata.

## Manual Happy Path

First create a campaign and one variant using existing APIs. Save `CAMPAIGN_ID` and `VARIANT_ID`.

### Observability Summary

```bash
curl http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/observability-summary
```

Expected: counts for traces, contexts, compliance results, tool calls, payloads, delivery logs, refinements, and evaluations.

### LLM Trace List

```bash
curl http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/llm-traces
```

Expected: trace previews with operation name, model, mock flag, status, latency, prompt preview, and response preview.

### LLM Trace Detail

```bash
curl http://localhost:8000/api/v1/llm-traces/TRACE_ID
```

Expected: full prompt, response, metadata, tokens, latency, status, and error if any.

### Tool Call List

```bash
curl http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/tool-calls
```

Expected: compliance rule/tool execution previews.

### Tool Call Detail

```bash
curl http://localhost:8000/api/v1/tool-calls/TOOL_CALL_ID
```

Expected: full input/output JSON, status, latency, and error.

### Debug Timeline

```bash
curl http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/debug-timeline
```

Expected: chronological compact events across chat, LLM, RAG, compliance, tools, approvals, payloads, delivery, refinements, and evaluations.

### Run Variant Evaluation

```bash
curl -X POST http://localhost:8000/api/v1/variants/VARIANT_ID/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"evaluation_type\":\"variant_quality\"}"
```

Expected: score, grade, passed flag, checks, recommendation, and saved `evaluation_id`.

### Run Readiness Evaluation

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/evaluate-readiness
```

Expected: campaign-level readiness score and checks.

### List Evaluations

```bash
curl http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/evaluations
```

Expected: saved variant and readiness evaluation rows.

### Evaluation Detail

```bash
curl http://localhost:8000/api/v1/evaluations/EVALUATION_ID
```

Expected: full saved evaluation result.

## Negative Tests

```bash
curl http://localhost:8000/api/v1/campaigns/camp_missing/observability-summary
curl http://localhost:8000/api/v1/llm-traces/trace_missing
curl http://localhost:8000/api/v1/tool-calls/tool_missing
curl http://localhost:8000/api/v1/evaluations/evalres_missing
curl -X POST http://localhost:8000/api/v1/variants/var_missing/evaluate -H "Content-Type: application/json" -d "{\"evaluation_type\":\"variant_quality\"}"
```

Expected: `RESOURCE_NOT_FOUND` envelopes.

## Manual Frontend Testing

1. Open `http://localhost:5173`.
2. Create a campaign.
3. Generate variants.
4. Run compliance on a variant.
5. Click `Refresh Debug Data`.
6. Confirm observability counts update.
7. Confirm trace/tool/timeline panels show entries.
8. Click `Run Evaluation` for a variant.
9. Confirm score, grade, recommendation, and evaluation history appear.
10. Click `Evaluate Readiness`.
11. Confirm a campaign readiness evaluation appears.

## DB Verification

```sql
select id, campaign_id, variant_id, evaluation_type, score, grade, passed, created_at
from evaluation_results
order by created_at desc;

select id, campaign_id, operation_name, status, created_at
from llm_traces
order by created_at desc;

select id, campaign_id, tool_name, status, created_at
from tool_call_logs
order by created_at desc;

select id, campaign_id, used_for, score, created_at
from retrieved_contexts
order by created_at desc;
```

## Troubleshooting

- If `evaluation_results` does not exist, run `uv run alembic upgrade head`.
- If LLM traces are empty, create a campaign and generate variants first.
- If tool calls are empty, run a compliance check.
- If frontend panels are empty, click `Refresh Debug Data`.
- Evaluation is advisory only; it will not change approval or send status.
