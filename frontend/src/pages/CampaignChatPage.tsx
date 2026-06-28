import { FormEvent, useState } from 'react';

import { CampaignPlanPanel } from '../components/campaign/CampaignPlanPanel';
import { CampaignBriefPreview } from '../components/campaign/CampaignBriefPreview';
import { ChatPanel } from '../components/chat/ChatPanel';
import { DocumentListPanel } from '../components/documents/DocumentListPanel';
import { DocumentUploadPanel } from '../components/documents/DocumentUploadPanel';
import { RetrievedContextPreview } from '../components/rag/RetrievedContextPreview';
import { VariantCardGrid } from '../components/variants/VariantCardGrid';
import { generateCampaignPlan, getRetrievedContext } from '../api/campaignApi';
import { sendCampaignChatMessage } from '../api/chatApi';
import { ingestDocument, listDocuments, uploadDocument } from '../api/documentApi';
import { generateCampaignVariants } from '../api/variantApi';
import type { CampaignBrief } from '../types/campaign';
import type { ConversationMessage } from '../types/chat';
import type { DocumentRecord } from '../types/document';
import type { RetrievedContext } from '../types/rag';
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
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
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
      if (response.retrieved_contexts?.length) {
        setContexts(response.retrieved_contexts as RetrievedContext[]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Variant generation failed.');
    } finally {
      setIsGenerating(false);
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

      <VariantCardGrid variants={variants} />
    </section>
  );
}
