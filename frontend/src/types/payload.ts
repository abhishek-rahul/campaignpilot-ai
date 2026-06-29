export type GeneratePayloadsRequest = {
  channels?: string[];
  regenerate?: boolean;
};

export type ChannelPayload = {
  payload_id: string;
  campaign_id: string;
  variant_id: string;
  channel: string;
  payload_type: string;
  payload_json: Record<string, unknown>;
  preview_text: string;
  status: string;
  error_message?: string | null;
  created_at: string;
  updated_at?: string | null;
};

export type GeneratePayloadsResponse = {
  campaign_id: string;
  selected_variant_id: string;
  payloads: ChannelPayload[];
};

export type PayloadListResponse = {
  campaign_id: string;
  payloads: ChannelPayload[];
};

export type PayloadReadiness = {
  campaign_id: string;
  ready: boolean;
  campaign_status: string | null;
  selected_variant_id: string | null;
  selected_variant_status: string | null;
  missing_requirements: string[];
};
