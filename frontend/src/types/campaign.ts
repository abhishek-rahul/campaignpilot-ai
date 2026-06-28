export type CampaignBrief = {
  goal: string | null;
  target_audience: string | null;
  offer_details: string | null;
  tone: string | null;
  preferred_channels: string[];
  cta_link: string | null;
  expiry_date: string | null;
  missing_fields: string[];
  brief_status: string;
};

export type CreateCampaignRequest = {
  campaign_name: string;
  goal?: string | null;
  target_audience?: string | null;
  offer_details?: string | null;
  tone?: string | null;
  preferred_channels?: string[];
  cta_link?: string | null;
  expiry_date?: string | null;
};

export type CampaignCreateData = {
  campaign_id: string;
  campaign_name: string;
  status: string;
  created_at: string;
};

export type CampaignDetail = {
  campaign_id: string;
  campaign_name: string;
  goal: string | null;
  target_audience: string | null;
  offer_details: string | null;
  tone: string | null;
  preferred_channels: string[];
  cta_link: string | null;
  expiry_date: string | null;
  status: string;
  brief_status: string | null;
  missing_fields: string[];
  created_at: string;
  updated_at: string;
};

export type CampaignUpdateData = {
  campaign_id: string;
  updated_fields: string[];
  status: string;
  updated_at: string;
};
