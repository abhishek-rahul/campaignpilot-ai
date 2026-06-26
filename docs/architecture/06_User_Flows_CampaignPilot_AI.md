# CampaignPilot AI - Phase 6 User Flows

Version: v0.1

This file is the implementation-friendly version of the Phase 6 user-flow diagram. Use it with `06_User_Flow_Diagram.png`.

## Core swimlanes

1. Campaign Manager / Frontend
2. Backend API & Campaign Service
3. AI Layer: LLM + RAG + Agent
4. Tools / Guardrails / Approval
5. Channels + Storage

## End-to-end flow

1. Campaign Manager opens Campaign Chat page.
2. Campaign Manager enters campaign idea in AI chat.
3. Campaign Manager uploads brand/product guideline documents.
4. Campaign Manager clicks **Generate Campaign Plan**.
5. `chat_routes.py` receives the chat message.
6. Document ingestion pipeline starts.
7. LLM extracts structured campaign brief: goal, target audience, offer, tone, CTA, preferred channels, missing fields.
8. System checks whether required campaign details are complete.
9. If details are incomplete, AI asks follow-up questions in streaming chat.
10. Document loader, text splitter, embedding service, and Elasticsearch vector store process uploaded docs.
11. Campaign Agent creates retrieval query.
12. RAG retrieves brand/product context from Elasticsearch.
13. Reranker selects top relevant chunks; LLM generates campaign strategy using retrieved context.
14. LLM generates 3-5 message variants with body, tone, channel, reason, used context reference.
15. Tool Registry runs compliance and guardrail checks: spam, PII, CTA, message length, banned words, misleading claim, brand rules, prompt injection.
16. System checks whether variant passed compliance.
17. If pass, mark variant ready for review.
18. If fail, show issues and suggestions to Campaign Manager, then re-run checks after refinement.
19. Campaign Manager reviews variants and compliance results.
20. Campaign Manager approves one variant or rejects/refines again.
21. System saves approval record and campaign status becomes APPROVED.
22. System generates channel-specific payload through Campaign Service -> Channel Registry -> Payload Mapper -> Channel Adapter.
23. TelegramSender sends approved message via Telegram Bot API.
24. MockWhatsAppSender generates WhatsApp template-style payload only.
25. System saves ChannelPayload and DeliveryLog in PostgreSQL.
26. Observability Service stores traces, tool calls, guardrail results, send status, and errors.
27. Evaluation Service can run RAG relevance, JSON validity, compliance correctness, prompt quality, and output safety tests.
28. Campaign Manager views delivery logs, trace summary, and evaluation results.

## Design rules

- Channels are pluggable. Core campaign logic must never call Telegram or WhatsApp directly.
- LangChain is used only behind wrappers in `llm/`, `rag/`, `tools/`, and `agents/`.
- Every non-streaming API must return the uniform `ApiResponse<T>` envelope.
- SSE streaming is the only normal response-envelope exception.
