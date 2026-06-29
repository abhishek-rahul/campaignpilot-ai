import { apiGet, apiPost } from './apiClient';
import type {
  ChannelPayload,
  GeneratePayloadsRequest,
  GeneratePayloadsResponse,
  PayloadListResponse,
  PayloadReadiness
} from '../types/payload';

export function getPayloadReadiness(campaignId: string): Promise<PayloadReadiness> {
  return apiGet<PayloadReadiness>(`/campaigns/${campaignId}/payload-readiness`);
}

export function generateChannelPayloads(
  campaignId: string,
  payload: GeneratePayloadsRequest
): Promise<GeneratePayloadsResponse> {
  return apiPost<GeneratePayloadsResponse>(`/campaigns/${campaignId}/payloads`, payload);
}

export function listCampaignPayloads(campaignId: string): Promise<PayloadListResponse> {
  return apiGet<PayloadListResponse>(`/campaigns/${campaignId}/payloads`);
}

export function getPayload(payloadId: string): Promise<ChannelPayload> {
  return apiGet<ChannelPayload>(`/payloads/${payloadId}`);
}
