# Slice 03 Understanding

## What Slice 3 Does

Slice 3 checks generated campaign message variants for simple compliance and brand risks, then lets a campaign manager approve or reject variants.

## End-to-End Flow

1. A campaign manager generates variants.
2. The manager clicks Run Compliance Check on a variant.
3. Backend loads the variant, campaign brief, and optional retrieved context.
4. Deterministic guardrail rules run.
5. Backend stores compliance result and tool-call logs.
6. Frontend displays status, risk, issues, and recommendation.
7. The manager approves or rejects the variant.
8. Backend stores an approval audit row and updates variant/campaign status.

## Backend Responsibilities

- `variant_routes.py`: exposes Slice 3 variant endpoints.
- `campaign_routes.py`: exposes campaign compliance summary.
- `compliance_service.py`: runs checks, saves results, updates variant status.
- `approval_service.py`: enforces approval rules and writes audit rows.
- `compliance_rules.py`: deterministic rule implementations.
- `guardrail_runner.py`: executes rules and aggregates risk.

## Frontend Responsibilities

- `VariantCompliancePanel.tsx`: per-variant compliance and approval controls.
- `CampaignComplianceSummary.tsx`: compact campaign-level summary.
- `VariantCardGrid.tsx`: renders variant cards with compliance controls.
- API files call the new backend endpoints through the common response handler.

## DB Tables Introduced

- `compliance_results`: saved result for each compliance run.
- `approvals`: human approval/rejection audit trail.
- `tool_call_logs`: one row per rule/tool execution.

## How Compliance Checks Work

The runner executes deterministic rules for misleading claims, urgency, expiry mention, CTA presence, offer consistency, emoji count, channel fit, and uploaded guideline context.

## Risk Scoring

- `PASSED` / `low`: no meaningful issues.
- `WARNING` / `medium`: non-blocking copy issues.
- `FAILED` / `high`: blocking misleading claim or inconsistent offer.

## Approval And Rejection

Approval requires a latest compliance result. Failed variants are blocked unless the request explicitly sets `allow_high_risk_override=true`. Rejection is always allowed for existing variants.

## Intentionally Not Implemented

Slice 3 does not send campaigns, generate channel payloads, add streaming, memory, evaluation dashboards, MCP, production auth, or external compliance integrations.
