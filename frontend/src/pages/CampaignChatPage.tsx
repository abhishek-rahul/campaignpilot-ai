import { FormEvent, useState } from 'react';

import { CampaignPlanPanel } from '../components/campaign/CampaignPlanPanel';
import { CampaignComplianceSummary } from '../components/campaign/CampaignComplianceSummary';
import { CampaignBriefPreview } from '../components/campaign/CampaignBriefPreview';
import { ChatPanel } from '../components/chat/ChatPanel';
import { DocumentListPanel } from '../components/documents/DocumentListPanel';
import { DocumentUploadPanel } from '../components/documents/DocumentUploadPanel';
import { DeliveryLogPanel } from '../components/delivery/DeliveryLogPanel';
import { EvaluationHistoryPanel } from '../components/evaluation/EvaluationHistoryPanel';
import { VariantEvaluationPanel } from '../components/evaluation/VariantEvaluationPanel';
import { DebugTimelinePanel } from '../components/observability/DebugTimelinePanel';
import { LlmTraceListPanel } from '../components/observability/LlmTraceListPanel';
import { ObservabilitySummaryPanel } from '../components/observability/ObservabilitySummaryPanel';
import { ToolCallLogPanel } from '../components/observability/ToolCallLogPanel';
import { PayloadGenerationPanel } from '../components/payloads/PayloadGenerationPanel';
import { PayloadPreviewPanel } from '../components/payloads/PayloadPreviewPanel';
import { PayloadReadinessPanel } from '../components/payloads/PayloadReadinessPanel';
import { BriefRefinementPanel } from '../components/refinements/BriefRefinementPanel';
import { RefinementHistoryPanel } from '../components/refinements/RefinementHistoryPanel';
import { VariantRefinementPanel } from '../components/refinements/VariantRefinementPanel';
import { RetrievedContextPreview } from '../components/rag/RetrievedContextPreview';
import { StreamingChatPanel } from '../components/chat/StreamingChatPanel';
import { VariantCardGrid } from '../components/variants/VariantCardGrid';
import { generateCampaignPlan, getCampaignComplianceSummary, getRetrievedContext } from '../api/campaignApi';
import { approveVariant, rejectVariant } from '../api/approvalApi';
import { sendCampaignChatMessage, sendCampaignChatMessageStream } from '../api/chatApi';
import { runVariantComplianceCheck } from '../api/complianceApi';
import { listCampaignDeliveryLogs, sendPayload } from '../api/deliveryApi';
import { ingestDocument, listDocuments, uploadDocument } from '../api/documentApi';
import { listCampaignEvaluations, runCampaignReadinessEvaluation, runVariantEvaluation } from '../api/evaluationApi';
import { getDebugTimeline, getObservabilitySummary, listLlmTraces, listToolCalls } from '../api/observabilityApi';
import { generateChannelPayloads, getPayloadReadiness, listCampaignPayloads } from '../api/payloadApi';
import {
  listCampaignRefinements,
  refineCampaignBrief,
  refineMessageVariant,
  regenerateCampaignVariants
} from '../api/refinementApi';
import { generateCampaignVariants } from '../api/variantApi';
import type { CampaignBrief } from '../types/campaign';
import type { ConversationMessage } from '../types/chat';
import type { DocumentRecord } from '../types/document';
import type { DeliveryLog } from '../types/delivery';
import type { EvaluationResult } from '../types/evaluation';
import type { DebugTimelineEvent, LlmTracePreview, ObservabilitySummary, ToolCallPreview } from '../types/observability';
import type { ChannelPayload, PayloadReadiness } from '../types/payload';
import type { RetrievedContext } from '../types/rag';
import type { CampaignComplianceSummary as ComplianceSummary, ComplianceResult } from '../types/compliance';
import type { RefineBriefResponse, RefinementRecord } from '../types/refinement';
import type { MessageVariant } from '../types/variant';

const samplePrompt =
  'Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June.';

export function CampaignChatPage() {
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const [message, setMessage] = useState(samplePrompt);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [brief, setBrief] = useState<CampaignBrief | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [contexts, setContexts] = useState<RetrievedContext[]>([]);
  const [plan, setPlan] = useState<Record<string, unknown> | null>(null);
  const [variants, setVariants] = useState<MessageVariant[]>([]);
  const [complianceByVariantId, setComplianceByVariantId] = useState<Record<string, ComplianceResult>>({});
  const [complianceSummary, setComplianceSummary] = useState<ComplianceSummary | null>(null);
  const [payloadReadiness, setPayloadReadiness] = useState<PayloadReadiness | null>(null);
  const [payloads, setPayloads] = useState<ChannelPayload[]>([]);
  const [deliveryLogs, setDeliveryLogs] = useState<DeliveryLog[]>([]);
  const [observabilitySummary, setObservabilitySummary] = useState<ObservabilitySummary | null>(null);
  const [llmTraces, setLlmTraces] = useState<LlmTracePreview[]>([]);
  const [toolCalls, setToolCalls] = useState<ToolCallPreview[]>([]);
  const [debugEvents, setDebugEvents] = useState<DebugTimelineEvent[]>([]);
  const [evaluations, setEvaluations] = useState<EvaluationResult[]>([]);
  const [evaluationByVariantId, setEvaluationByVariantId] = useState<Record<string, EvaluationResult>>({});
  const [refinements, setRefinements] = useState<RefinementRecord[]>([]);
  const [latestBriefRefinement, setLatestBriefRefinement] = useState<RefineBriefResponse | null>(null);
  const [streamingText, setStreamingText] = useState('');
  const [selectedPayloadChannels, setSelectedPayloadChannels] = useState<string[]>(['telegram', 'whatsapp_mock']);
  const [regeneratePayloads, setRegeneratePayloads] = useState(false);
  const [busyVariantId, setBusyVariantId] = useState<string | null>(null);
  const [isPayloadGenerating, setIsPayloadGenerating] = useState(false);
  const [sendingPayloadId, setSendingPayloadId] = useState<string | null>(null);
  const [isDebugLoading, setIsDebugLoading] = useState(false);
  const [evaluatingVariantId, setEvaluatingVariantId] = useState<string | null>(null);
  const [isReadinessEvaluating, setIsReadinessEvaluating] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefiningBrief, setIsRefiningBrief] = useState(false);
  const [isRefiningVariant, setIsRefiningVariant] = useState(false);
  const [isContextLoading, setIsContextLoading] = useState(false);
  const [isPlanLoading, setIsPlanLoading] = useState(false);
  const [ingestingDocumentId, setIngestingDocumentId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) {
      setError('Please enter a campaign message.');
      return;
    }
    setIsChatLoading(true);
    setError(null);
    const optimisticUserMessage: ConversationMessage = {
      message_id: `local_${Date.now()}`,
      sender: 'CAMPAIGN_MANAGER',
      message_text: message.trim(),
      message_type: 'text',
      created_at: new Date().toISOString()
    };
    try {
      const response = await sendCampaignChatMessage({
        campaign_id: campaignId,
        message: message.trim(),
        stream: false
      });
      setCampaignId(response.campaign_id);
      setBrief(response.campaign_brief);
      void refreshDocuments(response.campaign_id);
      void refreshPayloadState(response.campaign_id);
      void refreshRefinements(response.campaign_id);
      void refreshDebugData(response.campaign_id);
      setMessages((current) => [
        ...current,
        { ...optimisticUserMessage, message_id: response.conversation_message_id },
        {
          message_id: response.ai_message_id,
          sender: 'AI_AGENT',
          message_text: response.ai_reply,
          message_type: 'text',
          created_at: new Date().toISOString()
        }
      ]);
      setMessage('');
    } catch (err) {
      setMessages((current) => [...current, optimisticUserMessage]);
      setError(err instanceof Error ? err.message : 'Campaign chat failed.');
    } finally {
      setIsChatLoading(false);
    }
  }

  async function handleStreamingSubmit() {
    if (!message.trim()) {
      setError('Please enter a campaign message.');
      return;
    }
    const messageText = message.trim();
    const optimisticUserMessage: ConversationMessage = {
      message_id: `local_stream_${Date.now()}`,
      sender: 'CAMPAIGN_MANAGER',
      message_text: messageText,
      message_type: 'text',
      created_at: new Date().toISOString()
    };
    setIsStreaming(true);
    setStreamingText('');
    setError(null);
    setMessages((current) => [...current, optimisticUserMessage]);
    try {
      await sendCampaignChatMessageStream({ campaign_id: campaignId, message: messageText, stream: true }, (streamEvent) => {
        if (streamEvent.event === 'token') {
          setStreamingText((current) => `${current}${streamEvent.data.text}`);
        }
        if (streamEvent.event === 'brief_delta') {
          setBrief(streamEvent.data.campaign_brief);
        }
        if (streamEvent.event === 'final') {
          setCampaignId(streamEvent.data.campaign_id);
          setBrief(streamEvent.data.campaign_brief);
          setMessages((current) => [
            ...current.filter((item) => item.message_id !== optimisticUserMessage.message_id),
            { ...optimisticUserMessage, message_id: streamEvent.data.conversation_message_id },
            {
              message_id: streamEvent.data.ai_message_id,
              sender: 'AI_AGENT',
              message_text: streamEvent.data.ai_reply,
              message_type: 'text',
              created_at: new Date().toISOString()
            }
          ]);
          void refreshDocuments(streamEvent.data.campaign_id);
          void refreshPayloadState(streamEvent.data.campaign_id);
          void refreshRefinements(streamEvent.data.campaign_id);
          void refreshDebugData(streamEvent.data.campaign_id);
          setMessage('');
        }
        if (streamEvent.event === 'error') {
          setError(streamEvent.data.message);
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Streaming chat failed.');
    } finally {
      setIsStreaming(false);
    }
  }

  async function handleGenerateVariants(useRagContext = false) {
    if (!campaignId) {
      setError('Create a campaign brief first.');
      return;
    }
    setIsGenerating(true);
    setError(null);
    try {
      const response = await generateCampaignVariants(campaignId, {
        variant_count: 3,
        channels: brief?.preferred_channels.length ? brief.preferred_channels : undefined,
        use_rag_context: useRagContext,
        use_memory: false
      });
      setVariants(response.variants);
      await refreshComplianceSummary(campaignId);
      await refreshPayloadState(campaignId);
      await refreshDebugData(campaignId);
      if (response.retrieved_contexts?.length) {
        setContexts(response.retrieved_contexts as RetrievedContext[]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Variant generation failed.');
    } finally {
      setIsGenerating(false);
    }
  }

  async function refreshComplianceSummary(nextCampaignId = campaignId) {
    if (!nextCampaignId) return;
    try {
      const response = await getCampaignComplianceSummary(nextCampaignId);
      setComplianceSummary(response);
    } catch {
      setComplianceSummary(null);
    }
  }

  async function refreshPayloadState(nextCampaignId = campaignId) {
    if (!nextCampaignId) return;
    try {
      const [readinessResponse, payloadResponse, deliveryResponse] = await Promise.all([
        getPayloadReadiness(nextCampaignId),
        listCampaignPayloads(nextCampaignId),
        listCampaignDeliveryLogs(nextCampaignId)
      ]);
      setPayloadReadiness(readinessResponse);
      setPayloads(payloadResponse.payloads);
      setDeliveryLogs(deliveryResponse.delivery_logs);
    } catch {
      setPayloadReadiness(null);
    }
  }

  async function refreshRefinements(nextCampaignId = campaignId) {
    if (!nextCampaignId) return;
    try {
      const response = await listCampaignRefinements(nextCampaignId);
      setRefinements(response.refinements);
    } catch {
      setRefinements([]);
    }
  }

  async function refreshDebugData(nextCampaignId = campaignId) {
    if (!nextCampaignId) return;
    setIsDebugLoading(true);
    try {
      const [summaryResponse, traceResponse, toolResponse, timelineResponse, evaluationResponse] = await Promise.all([
        getObservabilitySummary(nextCampaignId),
        listLlmTraces(nextCampaignId),
        listToolCalls(nextCampaignId),
        getDebugTimeline(nextCampaignId),
        listCampaignEvaluations(nextCampaignId)
      ]);
      setObservabilitySummary(summaryResponse);
      setLlmTraces(traceResponse.traces);
      setToolCalls(toolResponse.tool_calls);
      setDebugEvents(timelineResponse.events);
      setEvaluations(evaluationResponse.evaluations);
      setEvaluationByVariantId(
        evaluationResponse.evaluations.reduce<Record<string, EvaluationResult>>((acc, evaluation) => {
          if (evaluation.variant_id && !acc[evaluation.variant_id]) {
            acc[evaluation.variant_id] = evaluation;
          }
          return acc;
        }, {})
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Debug data refresh failed.');
    } finally {
      setIsDebugLoading(false);
    }
  }

  async function handleRunCompliance(variantId: string) {
    setBusyVariantId(variantId);
    setError(null);
    try {
      const result = await runVariantComplianceCheck(variantId, { use_rag_context: true, include_llm_explanation: false });
      setComplianceByVariantId((current) => ({ ...current, [variantId]: result }));
      setVariants((current) =>
        current.map((variant) =>
          variant.variant_id === variantId
            ? {
                ...variant,
                risk_level: result.risk_level,
                status: result.status === 'FAILED' ? 'COMPLIANCE_FAILED' : 'COMPLIANCE_PASSED',
                latest_compliance_status: result.status,
                latest_compliance_result_id: result.compliance_result_id
              }
            : variant
        )
      );
      await refreshComplianceSummary();
      await refreshDebugData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Compliance check failed.');
    } finally {
      setBusyVariantId(null);
    }
  }

  async function handleApproveVariant(variantId: string, reason: string | null, allowHighRiskOverride: boolean) {
    setBusyVariantId(variantId);
    setError(null);
    try {
      const response = await approveVariant(variantId, { reason, allow_high_risk_override: allowHighRiskOverride });
      setVariants((current) =>
        current.map((variant) => (variant.variant_id === variantId ? { ...variant, status: response.new_status } : variant))
      );
      await refreshComplianceSummary();
      await refreshPayloadState();
      await refreshDebugData();
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Variant approval failed.');
    } finally {
      setBusyVariantId(null);
    }
  }

  async function handleRejectVariant(variantId: string, reason: string | null) {
    setBusyVariantId(variantId);
    setError(null);
    try {
      const response = await rejectVariant(variantId, { reason });
      setVariants((current) =>
        current.map((variant) => (variant.variant_id === variantId ? { ...variant, status: response.new_status } : variant))
      );
      await refreshComplianceSummary();
      await refreshPayloadState();
      await refreshDebugData();
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Variant rejection failed.');
    } finally {
      setBusyVariantId(null);
    }
  }

  async function refreshDocuments(nextCampaignId = campaignId) {
    try {
      const response = await listDocuments(nextCampaignId);
      setDocuments(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Document list failed.');
    }
  }

  async function handleUploadDocument(file: File, documentType: string) {
    if (!campaignId) {
      setError('Create a campaign before uploading campaign-specific documents.');
      return;
    }
    setError(null);
    try {
      const uploaded = await uploadDocument({ file, documentType, campaignId });
      setDocuments((current) => [uploaded, ...current.filter((item) => item.document_id !== uploaded.document_id)]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Document upload failed.');
    }
  }

  async function handleIngestDocument(documentId: string) {
    setIngestingDocumentId(documentId);
    setError(null);
    try {
      await ingestDocument(documentId);
      await refreshDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Document ingestion failed.');
      await refreshDocuments();
    } finally {
      setIngestingDocumentId(null);
    }
  }

  async function handleRefreshContext() {
    if (!campaignId) return;
    setIsContextLoading(true);
    setError(null);
    try {
      const response = await getRetrievedContext(campaignId, true);
      setContexts(response.contexts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Context retrieval failed.');
    } finally {
      setIsContextLoading(false);
    }
  }

  async function handleGeneratePlan() {
    if (!campaignId) return;
    setIsPlanLoading(true);
    setError(null);
    try {
      const response = await generateCampaignPlan(campaignId);
      setPlan(response.plan);
      setContexts(response.retrieved_contexts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Campaign plan failed.');
    } finally {
      setIsPlanLoading(false);
    }
  }

  function handleTogglePayloadChannel(channel: string) {
    setSelectedPayloadChannels((current) =>
      current.includes(channel) ? current.filter((item) => item !== channel) : [...current, channel]
    );
  }

  async function handleGeneratePayloads() {
    if (!campaignId) return;
    setIsPayloadGenerating(true);
    setError(null);
    try {
      const response = await generateChannelPayloads(campaignId, {
        channels: selectedPayloadChannels,
        regenerate: regeneratePayloads
      });
      setPayloads(response.payloads);
      await refreshPayloadState(campaignId);
      await refreshDebugData(campaignId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payload generation failed.');
    } finally {
      setIsPayloadGenerating(false);
    }
  }

  async function handleSendTelegramPayload(payloadId: string) {
    setSendingPayloadId(payloadId);
    setError(null);
    try {
      await sendPayload(payloadId);
      await refreshPayloadState();
      await refreshDebugData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Telegram send failed.');
      await refreshPayloadState();
    } finally {
      setSendingPayloadId(null);
    }
  }

  async function handleRefineBrief(feedback: string, useRagContext: boolean, apply: boolean) {
    if (!campaignId) return;
    setIsRefiningBrief(true);
    setError(null);
    try {
      const response = await refineCampaignBrief(campaignId, {
        feedback,
        use_rag_context: useRagContext,
        apply
      });
      setLatestBriefRefinement(response);
      setBrief(response.after_brief);
      await refreshRefinements(campaignId);
      await refreshPayloadState(campaignId);
      await refreshDebugData(campaignId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Brief refinement failed.');
    } finally {
      setIsRefiningBrief(false);
    }
  }

  async function handleRefineVariant(variantId: string, feedback: string, useRagContext: boolean) {
    setIsRefiningVariant(true);
    setError(null);
    try {
      const response = await refineMessageVariant(variantId, {
        feedback,
        use_rag_context: useRagContext,
        create_new_variant: true
      });
      setVariants((current) => [...current, response.refined_variant]);
      await refreshRefinements(response.campaign_id);
      await refreshDebugData(response.campaign_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Variant refinement failed.');
    } finally {
      setIsRefiningVariant(false);
    }
  }

  async function handleRegenerateVariantsFromFeedback(feedback: string, useRagContext: boolean) {
    if (!campaignId) return;
    setIsRefiningVariant(true);
    setError(null);
    try {
      const response = await regenerateCampaignVariants(campaignId, {
        feedback,
        variant_count: 3,
        channels: brief?.preferred_channels.length ? brief.preferred_channels : undefined,
        use_rag_context: useRagContext
      });
      setVariants((current) => [...current, ...response.variants]);
      await refreshRefinements(campaignId);
      await refreshDebugData(campaignId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Variant regeneration failed.');
    } finally {
      setIsRefiningVariant(false);
    }
  }

  async function handleRunVariantEvaluation(variantId: string) {
    setEvaluatingVariantId(variantId);
    setError(null);
    try {
      const response = await runVariantEvaluation(variantId);
      setEvaluationByVariantId((current) => ({ ...current, [variantId]: response }));
      await refreshDebugData(response.campaign_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Variant evaluation failed.');
    } finally {
      setEvaluatingVariantId(null);
    }
  }

  async function handleRunReadinessEvaluation() {
    if (!campaignId) return;
    setIsReadinessEvaluating(true);
    setError(null);
    try {
      await runCampaignReadinessEvaluation(campaignId);
      await refreshDebugData(campaignId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Readiness evaluation failed.');
    } finally {
      setIsReadinessEvaluating(false);
    }
  }

  const canGenerate = Boolean(campaignId && brief?.brief_status === 'COMPLETE');

  return (
    <section style={{ display: 'grid', gap: 18, marginTop: 16 }}>
      <form onSubmit={handleSubmit} style={{ border: '1px solid #d6d9de', borderRadius: 8, padding: 16 }}>
        <label htmlFor="campaign-message" style={{ display: 'block', fontWeight: 700, marginBottom: 8 }}>
          Campaign idea
        </label>
        <textarea
          id="campaign-message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={5}
          style={{ boxSizing: 'border-box', width: '100%', resize: 'vertical', padding: 10 }}
        />
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 12 }}>
          <button type="submit" disabled={isChatLoading} style={{ padding: '10px 14px' }}>
            {isChatLoading ? 'Sending...' : 'Send to AI'}
          </button>
          <button
            type="button"
            onClick={() => void handleStreamingSubmit()}
            disabled={isStreaming || isChatLoading}
            style={{ padding: '10px 14px' }}
          >
            {isStreaming ? 'Streaming...' : 'Send with Streaming'}
          </button>
          <button
            type="button"
            onClick={() => void handleGenerateVariants(false)}
            disabled={!canGenerate || isGenerating}
            style={{ padding: '10px 14px' }}
          >
            {isGenerating ? 'Generating...' : 'Generate Variants'}
          </button>
          <button
            type="button"
            onClick={() => void handleGenerateVariants(true)}
            disabled={!canGenerate || isGenerating}
            style={{ padding: '10px 14px' }}
          >
            {isGenerating ? 'Generating...' : 'Generate Variants with RAG'}
          </button>
          {campaignId && <span style={{ alignSelf: 'center', color: '#5d6675' }}>Campaign: {campaignId}</span>}
        </div>
        {error && <p style={{ color: '#b42318', marginBottom: 0 }}>{error}</p>}
      </form>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <ChatPanel messages={messages} />
        <CampaignBriefPreview brief={brief} />
      </div>

      <StreamingChatPanel text={streamingText} active={isStreaming} />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <DocumentUploadPanel disabled={!campaignId} onUpload={handleUploadDocument} />
        <DocumentListPanel documents={documents} onIngest={handleIngestDocument} loadingDocumentId={ingestingDocumentId} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <RetrievedContextPreview
          contexts={contexts}
          onRefresh={handleRefreshContext}
          disabled={!campaignId}
          loading={isContextLoading}
        />
        <CampaignPlanPanel plan={plan} onGenerate={handleGeneratePlan} disabled={!campaignId} loading={isPlanLoading} />
      </div>

      <CampaignComplianceSummary summary={complianceSummary} />

      <VariantCardGrid
        variants={variants}
        complianceByVariantId={complianceByVariantId}
        busyVariantId={busyVariantId}
        onRunCompliance={handleRunCompliance}
        onApprove={handleApproveVariant}
        onReject={handleRejectVariant}
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <BriefRefinementPanel
          disabled={!campaignId || !brief}
          loading={isRefiningBrief}
          result={latestBriefRefinement}
          onSubmit={handleRefineBrief}
        />
        <VariantRefinementPanel
          variants={variants}
          disabled={!campaignId || !brief}
          loading={isRefiningVariant}
          onRefineVariant={handleRefineVariant}
          onRegenerateVariants={handleRegenerateVariantsFromFeedback}
        />
      </div>

      <RefinementHistoryPanel refinements={refinements} />

      <ObservabilitySummaryPanel
        summary={observabilitySummary}
        loading={isDebugLoading}
        onRefresh={() => refreshDebugData()}
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <LlmTraceListPanel traces={llmTraces} />
        <ToolCallLogPanel toolCalls={toolCalls} />
      </div>

      <VariantEvaluationPanel
        variants={variants}
        latestByVariantId={evaluationByVariantId}
        busyVariantId={evaluatingVariantId}
        onEvaluate={handleRunVariantEvaluation}
        onEvaluateReadiness={handleRunReadinessEvaluation}
        readinessLoading={isReadinessEvaluating}
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <EvaluationHistoryPanel evaluations={evaluations} />
        <DebugTimelinePanel events={debugEvents} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <PayloadReadinessPanel readiness={payloadReadiness} />
        <PayloadGenerationPanel
          ready={Boolean(payloadReadiness?.ready)}
          selectedChannels={selectedPayloadChannels}
          regenerate={regeneratePayloads}
          loading={isPayloadGenerating}
          onToggleChannel={handleTogglePayloadChannel}
          onRegenerateChange={setRegeneratePayloads}
          onGenerate={() => void handleGeneratePayloads()}
        />
      </div>

      <PayloadPreviewPanel
        payloads={payloads}
        sendingPayloadId={sendingPayloadId}
        onSendTelegram={(payloadId) => void handleSendTelegramPayload(payloadId)}
      />

      <DeliveryLogPanel logs={deliveryLogs} />
    </section>
  );
}
