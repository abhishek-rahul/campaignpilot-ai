# Slice 03 Testing

## Setup Commands

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run python -m compileall app
uv run python -m pytest
```

If Windows temp permissions cause pytest issues:

```bash
uv run python -m pytest --basetemp %TEMP%\campaignpilot-pytest
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

## Curl Examples

Run compliance check:

```bash
curl -X POST http://localhost:8000/api/v1/variants/var_xxx/compliance-check \
  -H "Content-Type: application/json" \
  -d "{\"use_rag_context\":true,\"include_llm_explanation\":false}"
```

List compliance checks:

```bash
curl http://localhost:8000/api/v1/variants/var_xxx/compliance-checks
```

Approve variant:

```bash
curl -X POST http://localhost:8000/api/v1/variants/var_xxx/approve \
  -H "Content-Type: application/json" \
  -d "{\"reason\":\"Looks good\",\"allow_high_risk_override\":false}"
```

Reject variant:

```bash
curl -X POST http://localhost:8000/api/v1/variants/var_xxx/reject \
  -H "Content-Type: application/json" \
  -d "{\"reason\":\"Too aggressive\"}"
```

Campaign summary:

```bash
curl http://localhost:8000/api/v1/campaigns/camp_xxx/compliance-summary
```

## Manual Safe Variant Scenario

Use a generated friendly variant with the correct `25% discount`, CTA link, and expiry mention. Run compliance. Expected status: `PASSED` or `WARNING`. Approve it. Expected variant status: `APPROVED`.

## Manual Risky Variant Scenario

Patch a variant:

```bash
curl -X PATCH http://localhost:8000/api/v1/variants/var_xxx \
  -H "Content-Type: application/json" \
  -d "{\"message_body\":\"Last chance! Guaranteed savings with 50% discount. Hurry now!!! 🔥🔥🔥🔥\"}"
```

Run compliance. Expected status: `FAILED`, risk `high`.

Try approval without override. Expected error code: `VARIANT_NOT_COMPLIANT`.

Reject it. Expected variant status: `REJECTED`.

## Frontend Manual Steps

1. Create a campaign from chat.
2. Generate variants.
3. Click Run Compliance Check on a variant.
4. Confirm status, risk, issues, and recommendation render.
5. Approve a safe/warning variant.
6. Confirm status becomes `APPROVED`.
7. Edit a variant to risky copy through API or UI if available.
8. Run compliance.
9. Confirm failed result blocks normal approval.
10. Reject the risky variant.
11. Confirm summary counts update.

## DB Verification

```sql
select id, variant_id, status, risk_level, recommendation, created_at
from compliance_results
order by created_at desc;

select id, variant_id, approval_status, previous_status, new_status, override_used, created_at
from approvals
order by created_at desc;

select tool_name, status, latency_ms, created_at
from tool_call_logs
order by created_at desc;
```

## Troubleshooting

- Approval fails with `COMPLIANCE_CHECK_REQUIRED`: run compliance check first.
- Approval fails with `VARIANT_NOT_COMPLIANT`: latest check failed; reject or pass `allow_high_risk_override=true`.
- Integration tests skip: start Docker Postgres and run Alembic upgrade, or use a host-resolvable `DATABASE_URL`.
- This is not legal advice; the guardrails are deterministic demo checks.
