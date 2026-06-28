import { apiGet, apiPatch, apiPost } from './apiClient';
import type {
  GenerateVariantsRequest,
  GenerateVariantsResponse,
  UpdateVariantRequest,
  VariantListResponse,
  VariantUpdateResponse
} from '../types/variant';

export function generateCampaignVariants(
  campaignId: string,
  payload: GenerateVariantsRequest
): Promise<GenerateVariantsResponse> {
  return apiPost<GenerateVariantsResponse>(`/campaigns/${campaignId}/generate-variants`, payload);
}

export function listCampaignVariants(campaignId: string): Promise<VariantListResponse> {
  return apiGet<VariantListResponse>(`/campaigns/${campaignId}/variants`);
}

export function updateVariant(variantId: string, payload: UpdateVariantRequest): Promise<VariantUpdateResponse> {
  return apiPatch<VariantUpdateResponse>(`/variants/${variantId}`, payload);
}
