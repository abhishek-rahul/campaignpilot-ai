# Slice 02 Understanding

## What Slice 2 Does

Slice 2 lets CampaignPilot AI use uploaded brand or product documents as context for campaign planning and message variants.

The core flow is:

1. Create a campaign through the existing chat flow.
2. Upload a `.txt`, `.md`, or `.pdf` document for that campaign.
3. Ingest the document into chunks.
4. Create embeddings using OpenAI or deterministic mock embeddings.
5. Try to index chunks in Elasticsearch.
6. Retrieve relevant chunks for the campaign brief.
7. Generate a campaign plan or RAG-aware message variants.

## Backend Responsibilities

- `backend/app/api/routes/document_routes.py`: document upload, list, detail, and ingest endpoints.
- `backend/app/api/routes/campaign_routes.py`: retrieved context and campaign plan endpoints.
- `backend/app/services/document_service.py`: validates uploads, saves files, chunks text, embeds chunks, saves ingestion metadata.
- `backend/app/services/campaign_service.py`: retrieves context and generates campaign plans.
- `backend/app/services/variant_service.py`: keeps Slice 1 no-RAG generation and adds optional RAG context.
- `backend/app/rag/document_loader.py`: reads text, markdown, and PDF content.
- `backend/app/rag/text_splitter.py`: deterministic chunking.
- `backend/app/rag/embedding_client.py`: OpenAI or mock embeddings.
- `backend/app/rag/vector_store.py`: Elasticsearch indexing/search wrapper.
- `backend/app/rag/retriever.py`: builds campaign queries and falls back to DB lexical ranking.
- `backend/app/rag/rag_pipeline.py`: coordinates retrieval and saves retrieved contexts.

## Frontend Responsibilities

- `CampaignChatPage.tsx`: one page for Slice 1 chat plus Slice 2 document/RAG controls.
- `DocumentUploadPanel.tsx`: uploads a file and document type.
- `DocumentListPanel.tsx`: displays status, counts, and ingest action.
- `RetrievedContextPreview.tsx`: shows retrieved snippets.
- `CampaignPlanPanel.tsx`: generates and displays the campaign plan.
- `documentApi.ts`, `campaignApi.ts`, `variantApi.ts`: call backend APIs through the common envelope handler.

## DB Tables Introduced

- `brand_documents`: uploaded document metadata and ingestion status.
- `document_chunks`: chunk text and chunk metadata.
- `embedding_records`: embedding/index metadata per chunk.
- `retrieved_contexts`: saved retrieval results used for preview, plan generation, or variant generation.

## How Upload And Ingestion Work

The upload endpoint stores the file under the configured `UPLOAD_DIR` and creates a `brand_documents` row with status `UPLOADED`.

The ingest endpoint loads document text, creates chunks, embeds each chunk, attempts Elasticsearch indexing, creates `embedding_records`, and updates the document status to `INGESTED` or `FAILED`.

## How Retrieval Works

The retriever builds a query from the campaign brief: goal, audience, offer, tone, and channels. It tries Elasticsearch vector search first. If Elasticsearch is unavailable or has no result, it ranks ingested DB chunks with a simple lexical fallback.

Retrieved snippets are saved in `retrieved_contexts`.

## How Campaign Plan Works

`POST /api/v1/campaigns/{campaign_id}/plan` retrieves context, passes the campaign brief and snippets to the LLM wrapper, records an LLM trace, and returns a plan object. The plan is not persisted in Slice 2.

## How RAG Variants Work

`POST /api/v1/campaigns/{campaign_id}/generate-variants` keeps the old no-RAG behavior when `use_rag_context=false`. When `use_rag_context=true`, it retrieves and saves context first, then injects that context into the variant generation prompt.

## Mock Fallback

When `OPENAI_API_KEY` is missing, empty, or `replace_me`:

- Chat and variant generation use the existing mock LLM.
- Campaign plan generation uses a deterministic mock plan.
- Embeddings use deterministic hash vectors with dimension 384.

## Intentionally Not Implemented

Slice 2 does not implement compliance, approvals, delivery, Telegram sending, WhatsApp payload generation, streaming, memory, evaluation, observability dashboards, production auth, OCR, DOCX ingestion, or Slice 3+ agent workflows.
