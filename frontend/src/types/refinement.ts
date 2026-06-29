import type { CampaignBrief } from './campaign';
import type { MessageVariant } from './variant';

export type RefineBriefRequest = {
  feedback: string;
  use_rag_context?: boolean;
  apply?: boolean;
};

export type RefineVariantRequest = {
  feedback: string;
  use_rag_context?: boolean;
  create_new_variant?: boolean;
};

export type RegenerateVariantsRequest = {
  feedback: string;
  variant_count?: number;
  channels?: string[];
  use_rag_context?: boolean;
};

export type RefinementRecord = {
  refinement_id: string;
  campaign_id: string;
  source_type: string;
  source_id: string | null;
  refinement_type: string;
  user_feedback: string;
  before_json: Record<string, unknown>;
  after_json: Record<string, unknown>;
  status: string;
  llm_trace_id: string | null;
  created_at: string;
};

export type RefineBriefResponse = {
  campaign_id: string;
  refinement_id: string;
  applied: boolean;
  before_brief: CampaignBrief;
  after_brief: CampaignBrief;
  campaign_status: string;
  selected_variant_id: string | null;
};

export type RefineVariantResponse = {
  campaign_id: string;
  source_variant_id: string;
  refined_variant: MessageVariant;
  refinement_id: string;
  requires_compliance_check: boolean;
};

export type RegenerateVariantsResponse = {
  campaign_id: string;
  refinement_id: string;
  variants: MessageVariant[];
  requires_compliance_check: boolean;
};

export type RefinementListResponse = {
  campaign_id: string;
  refinements: RefinementRecord[];
};
