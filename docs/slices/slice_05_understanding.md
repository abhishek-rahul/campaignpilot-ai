# Slice 05 Understanding - Streaming Chat + Refinement Loop

## What Slice 5 Does

Slice 5 lets a campaign manager keep improving a campaign before launch. The user can stream a campaign chat response, refine the saved campaign brief, refine one generated variant into a new variant, regenerate variants from feedback, and see refinement history.

## End-to-End Flow

1. User submits a campaign idea with `Send with Streaming`.
2. Backend emits SSE events: `start`, multiple `token` events, `brief_delta`, and `final`.
3. Backend saves campaign, brief, conversation messages, and LLM trace.
4. User can refine the brief with feedback such as "make it premium and less pushy".
5. If the refinement is applied, `campaign_briefs` is updated and the action is saved in `campaign_refinements`.
6. User can refine a variant or regenerate variants from feedback.
7. New variants are saved as `GENERATED` and must go through compliance and approval again.

## Backend Files

- `backend/app/api/routes/chat_routes.py`: adds `POST /chat/campaign/stream`.
- `backend/app/api/routes/campaign_routes.py`: adds brief refinement, variant regeneration, and refinement history routes.
- `backend/app/api/routes/variant_routes.py`: adds variant refinement route.
- `backend/app/services/streaming_chat_service.py`: coordinates streaming chat and persistence.
- `backend/app/services/refinement_service.py`: handles brief refinement, variant refinement, regeneration, history, and safe reset rules.
- `backend/app/streaming/event_builder.py`: builds typed SSE frames.
- `backend/app/streaming/sse.py`: serializes SSE event/data frames.
- `backend/app/llm/llm_client.py`: keeps OpenAI/mock refinement behavior behind the LLM wrapper.

## Frontend Files

- `frontend/src/api/chatApi.ts`: adds streaming fetch/SSE parsing.
- `frontend/src/api/refinementApi.ts`: calls refinement endpoints through the shared response handler.
- `frontend/src/components/chat/StreamingChatPanel.tsx`: shows streaming token text.
- `frontend/src/components/refinements/BriefRefinementPanel.tsx`: captures brief feedback and apply mode.
- `frontend/src/components/refinements/VariantRefinementPanel.tsx`: refines selected variant or regenerates variants.
- `frontend/src/components/refinements/RefinementHistoryPanel.tsx`: displays saved refinement rows.
- `frontend/src/pages/CampaignChatPage.tsx`: wires Slice 5 into the existing one-page flow.

## DB Table Introduced

`campaign_refinements` stores:

- campaign id
- source type and source id
- refinement type
- user feedback
- before/after JSON snapshots
- status
- optional LLM trace id
- created timestamp

## Safe Reset Rule

If a brief is applied after a campaign has an approved or selected variant, the campaign is set to `NEEDS_REVIEW` and `selected_variant_id` is cleared. Old variants, compliance results, approvals, payloads, and delivery logs are not deleted.

## Mock Fallback

When `OPENAI_API_KEY` is empty, missing, or `replace_me`, mock LLM behavior is used:

- brief feedback containing `premium` changes tone to premium
- feedback like `less pushy` or `reduce urgency` softens the brief response
- variant feedback can make text shorter, softer, or more premium

## What Is Intentionally Not Implemented

- production observability dashboards
- persistent token-by-token event storage
- advanced memory system
- automatic compliance rerun
- automatic approval
- automatic payload generation
- automatic send
- scheduler or retry worker
- new delivery/channel behavior beyond preserving Slice 4
