# AI Editor Prompt - Start Slice 1

Use this prompt when asking an AI editor/code agent to implement Slice 1.

```text
You are working inside the CampaignPilot AI repository.

Before coding, read:
1. docs/master/00_MASTER_IMPLEMENTATION_GUIDE_CampaignPilot_AI.md
2. docs/architecture/07_API_Contract_CampaignPilot_AI_v3.docx
3. docs/architecture/08_DB_Schema_CampaignPilot_AI.docx
4. docs/architecture/06_User_Flows_CampaignPilot_AI.md

Implement ONLY Slice 1:
Campaign Chat + Brief Extraction + Variant Generation.

Scope:
- Backend FastAPI health must remain working.
- Implement campaign chat endpoint:
  POST /api/v1/chat/campaign
- Implement campaign endpoints required for Slice 1:
  POST /api/v1/campaigns
  GET /api/v1/campaigns
  GET /api/v1/campaigns/{campaign_id}
  PATCH /api/v1/campaigns/{campaign_id}
  GET /api/v1/campaigns/{campaign_id}/conversation
  POST /api/v1/campaigns/{campaign_id}/generate-variants
  GET /api/v1/campaigns/{campaign_id}/variants
  PATCH /api/v1/variants/{variant_id}
- Implement Slice 1 DB models only:
  campaign_managers
  campaigns
  campaign_briefs
  conversation_messages
  message_variants
  llm_traces
- Add Alembic migration only for Slice 1 tables.
- Implement LLM wrapper through backend/app/llm/llm_client.py only.
- Implement prompts in backend/app/llm/prompt_builder.py.
- Do not implement RAG, compliance, approval, channels, streaming, memory, evaluation, or Docker hardening beyond what already exists.
- All non-streaming APIs must follow the ApiResponse envelope:
  success, message, data, error, meta.
- Endpoint-specific data must be inside response.data only.
- Update frontend minimally for Slice 1:
  CampaignChatPage
  campaignApi.ts
  chatApi.ts
  variantApi.ts
  related types
- Add/update tests for Slice 1.
- After implementation, update docs/slices/slice_01_changes.md with implemented files, DB changes, API changes, testing steps, test evidence, known issues, and next slice notes.

Do not change the folder structure unless absolutely necessary. If a new file is required, put it inside the existing architecture folders.
```

## Backend Dependency Rule

The backend uses uv. Do not add backend/requirements.txt. Add or update dependencies only in backend/pyproject.toml, then run:

```bash
cd backend
uv sync --extra dev
uv run pytest
```
