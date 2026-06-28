import type { CampaignBrief } from './campaign';

export type CampaignChatRequest = {
  campaign_id: string | null;
  message: string;
  stream?: boolean;
};

export type CampaignChatResponse = {
  campaign_id: string;
  conversation_message_id: string;
  ai_message_id: string;
  ai_reply: string;
  brief_status: string;
  missing_fields: string[];
  campaign_brief: CampaignBrief;
};

export type ConversationMessage = {
  message_id: string;
  sender: string;
  message_text: string;
  message_type: string;
  created_at: string;
};

export type ConversationResponse = {
  campaign_id: string;
  messages: ConversationMessage[];
};
