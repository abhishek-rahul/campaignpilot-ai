# CampaignPilot AI - Master Implementation Guide

Version: v1.0 - Baseline Design + Vertical Slice Execution Plan

Purpose: Give this file to an AI editor before asking it to implement any vertical slice.

## AI Editor Rules

- Implement only the requested slice scope.

- Follow the final folder structure exactly.

- All non-streaming APIs return success, message, data, error, meta.

- Endpoint-specific fields always live inside response.data.

- SSE streaming is the only response-envelope exception.

- Do not import LangChain directly inside services/routes; use wrappers.

- Do not call Telegram/WhatsApp directly from Campaign Service; use Channel Registry.

- Do not create all tables at once; add tables by slice.

- After every slice, write docs/slices/slice_XX_changes.md.



## Baseline Phases 1-8

- Phase 1 Requirements: GenAI-heavy MVP scope.

- Phase 2 Domain Model: 21 core entities and relationships.

- Phase 3 Tech Stack: FastAPI, React/Vite, PostgreSQL, LangChain, OpenAI, Elasticsearch, Telegram, Docker.

- Phase 4 Channel & Tool Strategy: pluggable channels, internal tool registry, controlled LangChain, MCP later.

- Phase 5 HLD: frontend/backend/AI/storage/channel architecture.

- Phase 6 User Flows: chat -> RAG -> variants -> compliance -> approval -> channels -> logs/eval.

- Phase 7 API Contract: uniform ApiResponse<T> and endpoints.

- Phase 8 DB Schema: PostgreSQL + Elasticsearch schema introduced by slice.



## Final Folder Structure

```
campaignpilot-ai/
├── README.md
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── master/
│   │   └── 00_MASTER_IMPLEMENTATION_GUIDE_CampaignPilot_AI.docx
│   ├── architecture/
│   │   ├── 01_Requirements_CampaignPilot_AI.docx
│   │   ├── 02_Domain_Model_CampaignPilot_AI.docx
│   │   ├── 03_Tech_Stack_CampaignPilot_AI.docx
│   │   ├── 04_Channel_Tool_Strategy_CampaignPilot_AI.docx
│   │   ├── 05_HLD_CampaignPilot_AI.drawio
│   │   ├── 06_User_Flows_CampaignPilot_AI.docx
│   │   ├── 07_API_Contract_CampaignPilot_AI_v3.docx
│   │   └── 08_DB_Schema_CampaignPilot_AI.docx
│   └── slices/
│       ├── slice_01_changes.md
│       ├── slice_02_changes.md
│       ├── slice_03_changes.md
│       ├── slice_04_changes.md
│       ├── slice_05_changes.md
│       └── slice_06_changes.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   ├── dependencies.py
│       │   └── routes/
│       │       ├── health_routes.py
│       │       ├── campaign_routes.py
│       │       ├── chat_routes.py
│       │       ├── document_routes.py
│       │       ├── variant_routes.py
│       │       ├── compliance_routes.py
│       │       ├── approval_routes.py
│       │       ├── channel_routes.py
│       │       ├── delivery_routes.py
│       │       ├── observability_routes.py
│       │       ├── evaluation_routes.py
│       │       └── streaming_routes.py
│       ├── core/
│       │   ├── config.py
│       │   ├── constants.py
│       │   ├── exceptions.py
│       │   ├── ids.py
│       │   ├── logging.py
│       │   ├── response.py
│       │   └── security.py
│       ├── db/
│       │   ├── database.py
│       │   ├── session.py
│       │   ├── base.py
│       │   ├── models/
│       │   └── repositories/
│       ├── schemas/
│       │   ├── common_schema.py
│       │   ├── campaign_schema.py
│       │   ├── chat_schema.py
│       │   ├── document_schema.py
│       │   ├── variant_schema.py
│       │   ├── compliance_schema.py
│       │   ├── approval_schema.py
│       │   ├── channel_schema.py
│       │   ├── delivery_schema.py
│       │   ├── observability_schema.py
│       │   └── evaluation_schema.py
│       ├── services/
│       │   ├── campaign_service.py
│       │   ├── chat_service.py
│       │   ├── document_service.py
│       │   ├── variant_service.py
│       │   ├── compliance_service.py
│       │   ├── approval_service.py
│       │   ├── channel_service.py
│       │   ├── delivery_service.py
│       │   └── evaluation_service.py
│       ├── llm/
│       │   ├── llm_client.py
│       │   ├── prompt_builder.py
│       │   ├── structured_output.py
│       │   ├── streaming.py
│       │   └── model_router.py
│       ├── rag/
│       │   ├── document_loader.py
│       │   ├── text_splitter.py
│       │   ├── embedding_service.py
│       │   ├── vector_store.py
│       │   ├── retriever.py
│       │   ├── reranker.py
│       │   └── rag_pipeline.py
│       ├── agents/
│       │   └── campaign_agent.py
│       ├── tools/
│       │   ├── tool_registry.py
│       │   ├── compliance_tool.py
│       │   ├── campaign_tool.py
│       │   ├── rag_search_tool.py
│       │   ├── payload_builder_tool.py
│       │   └── messaging_tool.py
│       ├── guardrails/
│       │   ├── pii_guardrail.py
│       │   ├── spam_guardrail.py
│       │   ├── prompt_injection_guardrail.py
│       │   ├── output_validator.py
│       │   └── brand_rule_guardrail.py
│       ├── channels/
│       │   ├── base_channel.py
│       │   ├── channel_registry.py
│       │   ├── payload_mapper.py
│       │   ├── telegram/
│       │   │   ├── telegram_sender.py
│       │   │   ├── telegram_mapper.py
│       │   │   └── telegram_validator.py
│       │   └── whatsapp/
│       │       ├── mock_whatsapp_sender.py
│       │       ├── whatsapp_mapper.py
│       │       └── whatsapp_validator.py
│       ├── memory/
│       │   └── memory_service.py
│       ├── observability/
│       │   ├── trace_service.py
│       │   ├── token_tracker.py
│       │   └── observability_service.py
│       ├── evaluation/
│       │   ├── evaluation_runner.py
│       │   ├── rag_evaluator.py
│       │   ├── prompt_evaluator.py
│       │   ├── tool_evaluator.py
│       │   └── output_evaluator.py
│       ├── jobs/
│       │   ├── document_ingestion_job.py
│       │   └── send_campaign_job.py
│       ├── mcp/
│       │   └── README.md
│       └── utils/
│           ├── datetime_utils.py
│           └── json_utils.py
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        │   ├── apiClient.ts
        │   ├── response.ts
        │   ├── campaignApi.ts
        │   ├── chatApi.ts
        │   ├── documentApi.ts
        │   ├── variantApi.ts
        │   ├── complianceApi.ts
        │   ├── approvalApi.ts
        │   ├── channelApi.ts
        │   ├── deliveryApi.ts
        │   ├── observabilityApi.ts
        │   └── evaluationApi.ts
        ├── types/
        │   ├── common.ts
        │   ├── campaign.ts
        │   ├── chat.ts
        │   ├── document.ts
        │   ├── variant.ts
        │   ├── compliance.ts
        │   ├── channel.ts
        │   └── evaluation.ts
        ├── pages/
        │   ├── CampaignChatPage.tsx
        │   ├── CampaignDetailPage.tsx
        │   ├── DocumentUploadPage.tsx
        │   ├── VariantReviewPage.tsx
        │   ├── DeliveryLogsPage.tsx
        │   ├── ObservabilityPage.tsx
        │   └── EvaluationPage.tsx
        ├── components/
        │   ├── layout/
        │   ├── chat/
        │   ├── campaign/
        │   ├── documents/
        │   ├── variants/
        │   ├── compliance/
        │   ├── channels/
        │   └── common/
        ├── hooks/
        ├── routes/
        └── styles/
```

## Vertical Slices

### Slice 1: Campaign Chat + Brief Extraction + Variant Generation

Goal: Create the first working vertical flow: AI chat -> structured campaign brief -> saved campaign -> message variants -> frontend display.

Frontend: CampaignChatPage, chat input box and conversation panel, brief preview panel, Generate Variants button, variant cards/list

Backend: health_routes.py, chat_routes.py, campaign_routes.py, variant_routes.py, chat_service.py, campaign_service.py, variant_service.py, llm_client.py, prompt_builder.py, structured_output.py, trace_service.py

DB / Storage: campaign_managers, campaigns, campaign_briefs, conversation_messages, message_variants, llm_traces

APIs: GET /api/v1/health, POST /api/v1/chat/campaign, GET /api/v1/campaigns/{campaign_id}, GET /api/v1/campaigns/{campaign_id}/conversation, POST /api/v1/campaigns/{campaign_id}/generate-variants, GET /api/v1/campaigns/{campaign_id}/variants

GenAI Concepts: AI API, LLM, Prompt Engineering, Chat, Structured JSON output, Basic LLM tracing

Testing Steps:

1. Run backend unit tests for response envelope, prompt builder, structured output parser, campaign service, variant service.

1. Run API tests: health, chat campaign with new campaign_id=null, get campaign, get conversation, generate variants, list variants.

1. Verify DB rows are created in campaigns, campaign_briefs, conversation_messages, message_variants, llm_traces.

1. Verify frontend flow: type idea -> see AI reply -> see brief preview -> generate variants -> see variant cards.

1. Verify all non-streaming responses have success, message, data, error, meta.

1. Run npm build for frontend and pytest for backend.

Docs after slice: docs/slices/slice_01_changes.md, Update README with local run steps if changed., Document sample prompt and sample API response.

### Slice 2: Brand Guideline RAG

Goal: Make generation grounded in uploaded brand/product documents using Elasticsearch vector/hybrid retrieval.

Frontend: DocumentUploadPage, uploaded document list, ingestion status display, retrieved context preview in campaign detail or variant screen

Backend: document_routes.py, document_service.py, document_loader.py, text_splitter.py, embedding_service.py, vector_store.py, retriever.py, reranker.py, rag_pipeline.py, rag_search_tool.py

DB / Storage: brand_documents, document_chunks, embedding_records, retrieved_contexts, Elasticsearch index: campaignpilot_document_chunks

APIs: POST /api/v1/documents/upload, POST /api/v1/documents/{document_id}/ingest, GET /api/v1/documents, GET /api/v1/campaigns/{campaign_id}/retrieved-context, POST /api/v1/campaigns/{campaign_id}/plan optional

GenAI Concepts: Document loading, Chunking, Embeddings, Vector DB, Keyword/vector/hybrid retrieval, Reranking, RAG prompt assembly

Testing Steps:

1. Upload sample brand guideline file and verify brand_documents row.

1. Run ingest and verify chunks in PostgreSQL and Elasticsearch.

1. Search Elasticsearch directly for chunk records.

1. Generate variants with use_rag_context=true and verify RetrievedContext rows.

1. Verify variants mention/avoid rules from uploaded doc.

1. Run failure test for unsupported file type and ingestion failure envelope.

Docs after slice: docs/slices/slice_02_changes.md, Add sample brand guideline document under docs/sample_data or backend/tests/fixtures., Document chunking settings and embedding/index assumptions.

### Slice 3: Compliance Tools + Guardrails + Approval

Goal: Make every variant pass safety checks and require human approval before sending.

Frontend: VariantReviewPage, risk badges, compliance result panel, issues/suggestions list, Approve and Reject buttons

Backend: compliance_routes.py, approval_routes.py, compliance_service.py, approval_service.py, tool_registry.py, compliance_tool.py, pii_guardrail.py, spam_guardrail.py, prompt_injection_guardrail.py, output_validator.py, brand_rule_guardrail.py

DB / Storage: compliance_results, approvals, tool_call_logs, message_variants status updates, campaigns status updates

APIs: POST /api/v1/variants/{variant_id}/compliance-check, POST /api/v1/variants/{variant_id}/approve, POST /api/v1/variants/{variant_id}/reject, GET /api/v1/campaigns/{campaign_id}/tool-calls

GenAI Concepts: Tool Calling, Guardrails, Output validation, Human-in-the-loop approval, Tool call logging

Testing Steps:

1. Run compliance on low-risk variant and verify COMPLIANCE_PASSED.

1. Run compliance on spammy/PII variant and verify COMPLIANCE_FAILED with suggestions.

1. Try approving non-compliant variant and verify error code VARIANT_NOT_COMPLIANT.

1. Approve compliant variant and verify approval row and campaign status APPROVED.

1. Verify ToolCallLog exists for every tool execution.

1. Frontend: check approve/reject UI and issue display.

Docs after slice: docs/slices/slice_03_changes.md, Document compliance rule definitions and risk scoring., Add examples of passing/failing variants.

### Slice 4: Telegram Sending + Delivery Logs

Goal: Send approved Telegram messages through pluggable channel architecture and generate WhatsApp mock payloads.

Frontend: Channel selection UI, payload preview panel, Telegram Send button, WhatsApp mock payload preview, DeliveryLogsPage

Backend: channel_routes.py, delivery_routes.py, channel_service.py, delivery_service.py, base_channel.py, channel_registry.py, payload_mapper.py, telegram_sender.py, telegram_mapper.py, telegram_validator.py, mock_whatsapp_sender.py, whatsapp_mapper.py, whatsapp_validator.py, messaging_tool.py, payload_builder_tool.py

DB / Storage: channels, recipients, channel_payloads, delivery_logs, tool_call_logs optional

APIs: GET /api/v1/channels, POST /api/v1/campaigns/{campaign_id}/payloads, GET /api/v1/campaigns/{campaign_id}/payloads, POST /api/v1/campaigns/{campaign_id}/send, GET /api/v1/campaigns/{campaign_id}/delivery-logs

GenAI Concepts: Pluggable channel adapter pattern, External API integration, Payload generation, Delivery tracking

Testing Steps:

1. Seed one Telegram channel and one test recipient.

1. Generate payloads only after campaign APPROVED; verify CAMPAIGN_NOT_APPROVED error otherwise.

1. Verify Telegram payload mapper output.

1. Verify WhatsApp mock payload JSON and status MOCK_PAYLOAD_READY.

1. Run Telegram send with test token/chat_id or mocked provider and verify DeliveryLog.

1. Verify channel adapters are called through Channel Registry only.

1. Frontend: payload preview and delivery log table.

Docs after slice: docs/slices/slice_04_changes.md, Document Telegram setup steps in README., Document WhatsApp mock payload format.

### Slice 5: Streaming + Memory

Goal: Improve chat/refinement UX with SSE streaming and campaign/brand memory.

Frontend: Streaming chat UI, token-by-token response display, variant refinement chat, memory-aware refinement notice or debug panel

Backend: streaming_routes.py, llm/streaming.py, memory_service.py, chat_service.py updates, variant_service.py updates

DB / Storage: memory_profiles, additional conversation_messages, additional llm_traces

APIs: GET /api/v1/chat/campaign/{campaign_id}/stream, POST /api/v1/chat/campaign with stream=false remains supported, PATCH /api/v1/variants/{variant_id} for refined variants

GenAI Concepts: Streaming, Memory, Conversational refinement, Prompt context management

Testing Steps:

1. Open SSE endpoint and verify event: token, metadata, done events.

1. Trigger refinement: make variant shorter/friendly and verify updated message saved.

1. Create/update memory profile from approved style summary.

1. Verify future generation/refinement can read tone_preferences.

1. Verify stream error event shape on simulated LLM failure.

1. Frontend: response renders progressively without breaking existing non-stream chat.

Docs after slice: docs/slices/slice_05_changes.md, Document SSE event contract and memory behavior., Add examples of refinement instructions.

### Slice 6: Evaluation + Observability + Docker

Goal: Make the system traceable, testable, and runnable as a full local stack.

Frontend: ObservabilityPage, LLM traces view, tool call logs view, retrieved chunks view, evaluation result view

Backend: observability_routes.py, evaluation_routes.py, observability_service.py, evaluation_runner.py, rag_evaluator.py, prompt_evaluator.py, tool_evaluator.py, output_evaluator.py, Dockerfiles, docker-compose.yml

DB / Storage: evaluation_runs, evaluation_results, operational indexes for traces/logs

APIs: GET /api/v1/campaigns/{campaign_id}/llm-traces, GET /api/v1/campaigns/{campaign_id}/tool-calls, GET /api/v1/campaigns/{campaign_id}/retrieved-context, POST /api/v1/evaluations/run, GET /api/v1/evaluations/{evaluation_run_id}

GenAI Concepts: Evaluation, Observability, Tracing, RAG quality checks, Prompt quality checks, Deployment

Testing Steps:

1. Run end-to-end campaign flow from chat to logs.

1. Run evaluation and verify evaluation_runs/evaluation_results rows.

1. Verify observability pages show LLMTrace, ToolCallLog, RetrievedContext, DeliveryLog summaries.

1. Run docker compose up and verify backend, frontend, PostgreSQL, Elasticsearch are reachable.

1. Run smoke tests against /health, /campaigns, /documents, /evaluations.

1. Document final local setup and teardown.

Docs after slice: docs/slices/slice_06_changes.md, Update root README with full Docker run steps., Document evaluation test cases and observability fields.

## Slice Change Document Template

```
# Slice XX Changes - <Slice Name>

## 1. Summary
## 2. User-visible Features
## 3. Backend Changes
## 4. Frontend Changes
## 5. DB / Migration Changes
## 6. API Contract Implemented
## 7. GenAI Components Implemented
## 8. Testing Evidence
## 9. Known Limitations
## 10. Next Slice Handoff
```
