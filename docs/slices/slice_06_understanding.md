# Slice 06 Understanding - Observability + Evaluation

## What Slice 6 Does

Slice 6 makes CampaignPilot easier to debug. It exposes records already created by earlier slices, such as LLM traces, RAG contexts, compliance tool calls, payloads, deliveries, and refinements. It also adds simple deterministic evaluation results for variants and campaign readiness.

## End-to-End Debug Flow

1. Create a campaign through normal or streaming chat.
2. Generate variants and optionally use RAG.
3. Run compliance and approval.
4. Generate payloads and optionally send Telegram.
5. Refine brief or variants.
6. Open the debug panels to inspect counts, traces, tool calls, timeline, and evaluations.

## Backend Responsibilities

- `observability_service.py`: builds summary counts, LLM trace previews/details, tool call previews/details, and debug timeline.
- `evaluation_service.py`: runs deterministic variant and readiness evaluations and saves results.
- `observability_repository.py`: runs read-only aggregation/timeline queries.
- `evaluation_repository.py`: persists and reads `evaluation_results`.
- `variant_quality.py`: contains the advisory variant quality rules.

## Frontend Responsibilities

- `observabilityApi.ts`: reads summary, traces, tool calls, and timeline.
- `evaluationApi.ts`: runs variant/readiness evaluation and lists evaluation history.
- Observability components render debug counts and compact previews.
- Evaluation components render scores, grades, checks, and recommendations.

## DB Table Introduced

`evaluation_results` stores:

- campaign id
- optional variant id
- evaluation type
- score
- grade
- pass/fail
- checks JSON
- recommendation
- created timestamp

## Observability Summary

The summary counts existing rows by campaign:

- LLM traces
- retrieved contexts
- compliance results
- tool calls
- payloads
- delivery logs
- refinements
- evaluations

It also returns latest activity timestamps for traces, tool calls, delivery, refinements, and evaluations.

## LLM Trace Inspection

Campaign trace list returns compact previews. Trace detail returns full prompt, response text, metadata, token counts, latency, status, and errors.

## Tool Call Inspection

Campaign tool-call list returns compact compliance/tool execution previews. Tool-call detail returns full input/output JSON, status, latency, and error information.

## Debug Timeline

The timeline combines compact events from chat messages, traces, retrieved contexts, compliance results, tool calls, approvals, payloads, delivery logs, refinements, and evaluations. It is chronological and intentionally preview-oriented.

## Evaluation

Variant evaluation checks CTA, message length, tone alignment, offer presence, aggressive urgency, and high-risk claim hints. Readiness evaluation checks whether campaign launch artifacts exist. Evaluation is advisory only; it never changes variant status or sends anything.

## Intentionally Not Implemented

- `evaluation_runs`
- LLM-as-judge
- production analytics dashboard
- auth/permissions
- scheduler/background jobs
- real WhatsApp sending
- automatic approval, rejection, or send
