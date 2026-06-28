import { apiGet, apiPatch, apiPost } from './apiClient';
import type {
  CampaignCreateData,
  CampaignDetail,
  CampaignUpdateData,
  CreateCampaignRequest
} from '../types/campaign';

export function createCampaign(payload: CreateCampaignRequest): Promise<CampaignCreateData> {
  return apiPost<CampaignCreateData>('/campaigns', payload);
}

export function getCampaign(campaignId: string): Promise<CampaignDetail> {
  return apiGet<CampaignDetail>(`/campaigns/${campaignId}`);
}

export function updateCampaign(
  campaignId: string,
  payload: Partial<CreateCampaignRequest>
): Promise<CampaignUpdateData> {
  return apiPatch<CampaignUpdateData>(`/campaigns/${campaignId}`, payload);
}
