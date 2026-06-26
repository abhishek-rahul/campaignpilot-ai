from pathlib import Path

root = Path("campaignpilot-ai")

dirs = [
    "docs/master",
    "docs/architecture",
    "docs/slices",

    "backend/alembic/versions",
    "backend/tests/unit",
    "backend/tests/integration",
    "backend/tests/e2e",
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/db/models",
    "backend/app/db/repositories",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/llm",
    "backend/app/rag",
    "backend/app/agents",
    "backend/app/tools",
    "backend/app/guardrails",
    "backend/app/channels/telegram",
    "backend/app/channels/whatsapp",
    "backend/app/memory",
    "backend/app/observability",
    "backend/app/evaluation",
    "backend/app/jobs",
    "backend/app/mcp",
    "backend/app/utils",

    "frontend/src/api",
    "frontend/src/types",
    "frontend/src/pages",
    "frontend/src/components/layout",
    "frontend/src/components/chat",
    "frontend/src/components/campaign",
    "frontend/src/components/documents",
    "frontend/src/components/variants",
    "frontend/src/components/compliance",
    "frontend/src/components/channels",
    "frontend/src/components/common",
    "frontend/src/hooks",
    "frontend/src/routes",
    "frontend/src/styles",
]

files = [
    "README.md",
    "docker-compose.yml",
    ".env.example",

    "docs/master/00_MASTER_IMPLEMENTATION_GUIDE_CampaignPilot_AI.docx",
    "docs/architecture/01_Requirements_CampaignPilot_AI.docx",
    "docs/architecture/02_Domain_Model_CampaignPilot_AI.docx",
    "docs/architecture/03_Tech_Stack_CampaignPilot_AI.docx",
    "docs/architecture/04_Channel_Tool_Strategy_CampaignPilot_AI.docx",
    "docs/architecture/05_HLD_CampaignPilot_AI.drawio",
    "docs/architecture/06_User_Flows_CampaignPilot_AI.docx",
    "docs/architecture/07_API_Contract_CampaignPilot_AI_v3.docx",
    "docs/architecture/08_DB_Schema_CampaignPilot_AI.docx",
    "docs/slices/slice_01_changes.md",
    "docs/slices/slice_02_changes.md",
    "docs/slices/slice_03_changes.md",
    "docs/slices/slice_04_changes.md",
    "docs/slices/slice_05_changes.md",
    "docs/slices/slice_06_changes.md",

    "backend/Dockerfile",
    "backend/requirements.txt",
    "backend/alembic.ini",
    "backend/alembic/env.py",
    "backend/app/main.py",

    "backend/app/api/dependencies.py",
    "backend/app/api/routes/health_routes.py",
    "backend/app/api/routes/campaign_routes.py",
    "backend/app/api/routes/chat_routes.py",
    "backend/app/api/routes/document_routes.py",
    "backend/app/api/routes/variant_routes.py",
    "backend/app/api/routes/compliance_routes.py",
    "backend/app/api/routes/approval_routes.py",
    "backend/app/api/routes/channel_routes.py",
    "backend/app/api/routes/delivery_routes.py",
    "backend/app/api/routes/observability_routes.py",
    "backend/app/api/routes/evaluation_routes.py",
    "backend/app/api/routes/streaming_routes.py",

    "backend/app/core/config.py",
    "backend/app/core/constants.py",
    "backend/app/core/exceptions.py",
    "backend/app/core/ids.py",
    "backend/app/core/logging.py",
    "backend/app/core/response.py",
    "backend/app/core/security.py",

    "backend/app/db/database.py",
    "backend/app/db/session.py",
    "backend/app/db/base.py",

    "backend/app/schemas/common_schema.py",
    "backend/app/schemas/campaign_schema.py",
    "backend/app/schemas/chat_schema.py",
    "backend/app/schemas/document_schema.py",
    "backend/app/schemas/variant_schema.py",
    "backend/app/schemas/compliance_schema.py",
    "backend/app/schemas/approval_schema.py",
    "backend/app/schemas/channel_schema.py",
    "backend/app/schemas/delivery_schema.py",
    "backend/app/schemas/observability_schema.py",
    "backend/app/schemas/evaluation_schema.py",

    "backend/app/services/campaign_service.py",
    "backend/app/services/chat_service.py",
    "backend/app/services/document_service.py",
    "backend/app/services/variant_service.py",
    "backend/app/services/compliance_service.py",
    "backend/app/services/approval_service.py",
    "backend/app/services/channel_service.py",
    "backend/app/services/delivery_service.py",
    "backend/app/services/evaluation_service.py",

    "backend/app/llm/llm_client.py",
    "backend/app/llm/prompt_builder.py",
    "backend/app/llm/structured_output.py",
    "backend/app/llm/streaming.py",
    "backend/app/llm/model_router.py",

    "backend/app/rag/document_loader.py",
    "backend/app/rag/text_splitter.py",
    "backend/app/rag/embedding_service.py",
    "backend/app/rag/vector_store.py",
    "backend/app/rag/retriever.py",
    "backend/app/rag/reranker.py",
    "backend/app/rag/rag_pipeline.py",

    "backend/app/agents/campaign_agent.py",

    "backend/app/tools/tool_registry.py",
    "backend/app/tools/compliance_tool.py",
    "backend/app/tools/campaign_tool.py",
    "backend/app/tools/rag_search_tool.py",
    "backend/app/tools/payload_builder_tool.py",
    "backend/app/tools/messaging_tool.py",

    "backend/app/guardrails/pii_guardrail.py",
    "backend/app/guardrails/spam_guardrail.py",
    "backend/app/guardrails/prompt_injection_guardrail.py",
    "backend/app/guardrails/output_validator.py",
    "backend/app/guardrails/brand_rule_guardrail.py",

    "backend/app/channels/base_channel.py",
    "backend/app/channels/channel_registry.py",
    "backend/app/channels/payload_mapper.py",
    "backend/app/channels/telegram/telegram_sender.py",
    "backend/app/channels/telegram/telegram_mapper.py",
    "backend/app/channels/telegram/telegram_validator.py",
    "backend/app/channels/whatsapp/mock_whatsapp_sender.py",
    "backend/app/channels/whatsapp/whatsapp_mapper.py",
    "backend/app/channels/whatsapp/whatsapp_validator.py",

    "backend/app/memory/memory_service.py",

    "backend/app/observability/trace_service.py",
    "backend/app/observability/token_tracker.py",
    "backend/app/observability/observability_service.py",

    "backend/app/evaluation/evaluation_runner.py",
    "backend/app/evaluation/rag_evaluator.py",
    "backend/app/evaluation/prompt_evaluator.py",
    "backend/app/evaluation/tool_evaluator.py",
    "backend/app/evaluation/output_evaluator.py",

    "backend/app/jobs/document_ingestion_job.py",
    "backend/app/jobs/send_campaign_job.py",

    "backend/app/mcp/README.md",

    "backend/app/utils/datetime_utils.py",
    "backend/app/utils/json_utils.py",

    "frontend/Dockerfile",
    "frontend/package.json",
    "frontend/vite.config.ts",
    "frontend/src/main.tsx",
    "frontend/src/App.tsx",

    "frontend/src/api/apiClient.ts",
    "frontend/src/api/response.ts",
    "frontend/src/api/campaignApi.ts",
    "frontend/src/api/chatApi.ts",
    "frontend/src/api/documentApi.ts",
    "frontend/src/api/variantApi.ts",
    "frontend/src/api/complianceApi.ts",
    "frontend/src/api/approvalApi.ts",
    "frontend/src/api/channelApi.ts",
    "frontend/src/api/deliveryApi.ts",
    "frontend/src/api/observabilityApi.ts",
    "frontend/src/api/evaluationApi.ts",

    "frontend/src/types/common.ts",
    "frontend/src/types/campaign.ts",
    "frontend/src/types/chat.ts",
    "frontend/src/types/document.ts",
    "frontend/src/types/variant.ts",
    "frontend/src/types/compliance.ts",
    "frontend/src/types/channel.ts",
    "frontend/src/types/evaluation.ts",

    "frontend/src/pages/CampaignChatPage.tsx",
    "frontend/src/pages/CampaignDetailPage.tsx",
    "frontend/src/pages/DocumentUploadPage.tsx",
    "frontend/src/pages/VariantReviewPage.tsx",
    "frontend/src/pages/DeliveryLogsPage.tsx",
    "frontend/src/pages/ObservabilityPage.tsx",
    "frontend/src/pages/EvaluationPage.tsx",
]

for d in dirs:
    (root / d).mkdir(parents=True, exist_ok=True)

for f in files:
    path = root / f
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

# Python packages ke liye __init__.py files
python_dirs = [
    "backend/app",
    "backend/app/api",
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/db",
    "backend/app/db/models",
    "backend/app/db/repositories",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/llm",
    "backend/app/rag",
    "backend/app/agents",
    "backend/app/tools",
    "backend/app/guardrails",
    "backend/app/channels",
    "backend/app/channels/telegram",
    "backend/app/channels/whatsapp",
    "backend/app/memory",
    "backend/app/observability",
    "backend/app/evaluation",
    "backend/app/jobs",
    "backend/app/utils",
]

for d in python_dirs:
    (root / d / "__init__.py").touch(exist_ok=True)

print(f"Created folder structure at: {root.resolve()}")