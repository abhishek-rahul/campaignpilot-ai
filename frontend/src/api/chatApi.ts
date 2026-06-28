import { apiGet, apiPost } from './apiClient';
import type { CampaignChatRequest, CampaignChatResponse, ConversationResponse } from '../types/chat';

export function sendCampaignChatMessage(payload: CampaignChatRequest): Promise<CampaignChatResponse> {
  return apiPost<CampaignChatResponse>('/chat/campaign', payload);
}

export function getCampaignConversation(campaignId: string): Promise<ConversationResponse> {
  return apiGet<ConversationResponse>(`/campaigns/${campaignId}/conversation`);
}
