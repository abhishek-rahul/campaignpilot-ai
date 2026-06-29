# Slice 05 Changes - Streaming Chat + Refinement Loop

## Summary

Slice 5 adds an interactive refinement loop on top of Slices 1-4. Campaign managers can use SSE streaming chat, refine the structured campaign brief from feedback, refine a selected variant into a new variant, regenerate variants from feedback, and view refinement history.

## User-Visible Features

- New `Send with Streaming` chat action that streams AI response tokens.
- Brief refinement panel with RAG toggle and apply/proposal mode.
- Variant refinement panel for refining a selected variant or regenerating variants from feedback.
- Refinement history panel showing feedback, source, status, and timestamp.
- Applied brief refinement resets approved/selected state to `NEEDS_REVIEW` so compliance, approval, payloads, and send are rerun intentionally.

## Backend Changes

- Added `POST /api/v1/chat/campaign/stream` as an SSE endpoint.
- Added `POST /api/v1/campaigns/{campaign_id}/refine-brief`.
- Added `POST /api/v1/variants/{variant_id}/refine`.
- Added `POST /api/v1/campaigns/{campaign_id}/regenerate-variants`.
- Added `GET /api/v1/campaigns/{campaign_id}/refinements`.
- Added `refinement_service.py` and `streaming_chat_service.py`.
- Added reusable SSE helpers under `backend/app/streaming/`.
- Extended the LLM wrapper with brief refinement, variant refinement, and mock fallback behavior.

## Frontend Changes

- Added streaming chat client and `StreamingChatPanel`.
- Added `refinementApi.ts` and `types/refinement.ts`.
- Added `BriefRefinementPanel`, `VariantRefinementPanel`, and `RefinementHistoryPanel`.
- Extended `CampaignChatPage.tsx` while keeping the existing Slice 1-4 workflow intact.

## DB/Migration Changes

- Added Alembic migration `005_slice_5_streaming_refinement.py`.
- Added table `campaign_refinements`.
- No streaming event table, memory table, evaluation table, scheduler table, or channel/delivery table changes were added in this slice.

## API Contract

- Non-streaming refinement endpoints use the standard ApiResponse envelope.
- The streaming endpoint intentionally returns `text/event-stream` frames instead of the JSON envelope.
- SSE events currently include `start`, `token`, `brief_delta`, `final`, and `error`.

## GenAI Components

- Real OpenAI calls remain behind `backend/app/llm/llm_client.py`.
- Mock fallback remains mandatory when `OPENAI_API_KEY` is missing, empty, or `replace_me`.
- Mock fallback supports deterministic brief refinement and variant refinement.
- LLM traces are recorded for `streaming_brief_extraction`, `brief_refinement`, `variant_refinement`, and `variant_regeneration`.

## Testing Evidence

- `docker compose exec -T backend uv run alembic upgrade head`: passed and applied `004_slice_4 -> 005_slice_5`.
- `docker compose exec -T backend uv run python -m compileall app`: passed.
- `docker compose exec -T backend uv run python -m pytest --basetemp /tmp/campaignpilot-pytest`: 56 passed.
- `cd frontend && npm install`: passed.
- `cd frontend && npm run build`: passed.
- `curl http://localhost:8000/api/v1/health`: passed.
- `curl http://localhost:9200`: passed after Elasticsearch finished startup.

## Known Limitations

- Real OpenAI streaming is not a separate token-by-token provider path yet; local reliability is provided through deterministic mock streaming.
- Streaming chat persists the final conversation, brief, and trace, but does not persist individual token events.
- Refinement does not auto-run compliance, approval, payload generation, or send.
- Existing payloads and delivery logs remain historical after refinement.

## Next Slice Handoff Notes

- Slice 6 can build public observability/reporting over `llm_traces`, `tool_call_logs`, and `campaign_refinements`.
- If production-grade streaming is needed, add provider-native streaming behind the LLM wrapper without changing route/business service imports.
