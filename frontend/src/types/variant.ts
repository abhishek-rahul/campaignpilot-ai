export type GenerateVariantsRequest = {
  variant_count: number;
  channels?: string[];
  use_rag_context?: boolean;
  use_memory?: boolean;
};

export type MessageVariant = {
  variant_id: string;
  variant_name: string;
  channel: string;
  message_body: string;
  tone: string | null;
  reason: string | null;
  risk_level: string | null;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
};

export type VariantListResponse = {
  campaign_id: string;
  variants: MessageVariant[];
};

export type GenerateVariantsResponse = VariantListResponse;

export type UpdateVariantRequest = {
  variant_name?: string | null;
  message_body?: string | null;
  tone?: string | null;
  reason?: string | null;
  risk_level?: string | null;
};

export type VariantUpdateResponse = {
  variant_id: string;
  updated_fields: string[];
  status: string;
  updated_at: string;
};
