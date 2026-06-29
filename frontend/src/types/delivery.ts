export type DeliveryLog = {
  delivery_id: string;
  payload_id: string;
  campaign_id: string;
  variant_id: string;
  channel: string;
  status: string;
  provider: string;
  provider_message_id?: string | null;
  request_json?: Record<string, unknown> | null;
  response_json?: Record<string, unknown> | null;
  error_message?: string | null;
  sent_at?: string | null;
  created_at: string;
};

export type SendPayloadResponse = {
  delivery_id: string;
  payload_id: string;
  campaign_id: string;
  variant_id: string;
  channel: string;
  status: string;
  provider: string;
  provider_message_id?: string | null;
  error_message?: string | null;
  sent_at?: string | null;
  created_at: string;
};

export type DeliveryLogListResponse = {
  campaign_id: string;
  delivery_logs: DeliveryLog[];
};
