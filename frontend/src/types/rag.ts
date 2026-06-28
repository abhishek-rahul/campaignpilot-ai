export type RetrievedContext = {
  context_id: string;
  campaign_id: string;
  document_id: string | null;
  chunk_id: string | null;
  query_text: string;
  retrieved_text: string;
  score: number | null;
  rank_position: number;
  source_type: string;
  used_for: string;
  metadata: Record<string, unknown>;
  created_at?: string | null;
};

export type RetrievedContextResponse = {
  campaign_id: string;
  contexts: RetrievedContext[];
};

export type CampaignPlanResponse = {
  campaign_id: string;
  plan: Record<string, unknown>;
  retrieved_contexts: RetrievedContext[];
};
