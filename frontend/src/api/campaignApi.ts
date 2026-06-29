import { apiGet, apiPatch, apiPost } from './apiClient';
import type {
  CampaignCreateData,
  CampaignDetail,
  CampaignUpdateData,
  CreateCampaignRequest
} from '../types/campaign';
import type { CampaignPlanResponse, RetrievedContextResponse } from '../types/rag';
import type { CampaignComplianceSummary } from '../types/compliance';

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

export function getRetrievedContext(campaignId: string, refresh = false): Promise<RetrievedContextResponse> {
  return apiGet<RetrievedContextResponse>(`/campaigns/${campaignId}/retrieved-context?refresh=${refresh}`);
}

export function generateCampaignPlan(campaignId: string): Promise<CampaignPlanResponse> {
  return apiPost<CampaignPlanResponse>(`/campaigns/${campaignId}/plan`);
}

export function getCampaignComplianceSummary(campaignId: string): Promise<CampaignComplianceSummary> {
  return apiGet<CampaignComplianceSummary>(`/campaigns/${campaignId}/compliance-summary`);
}
