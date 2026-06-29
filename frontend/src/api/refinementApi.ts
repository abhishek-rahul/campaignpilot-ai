import { apiGet, apiPost } from './apiClient';
import type {
  RefineBriefRequest,
  RefineBriefResponse,
  RefineVariantRequest,
  RefineVariantResponse,
  RefinementListResponse,
  RegenerateVariantsRequest,
  RegenerateVariantsResponse
} from '../types/refinement';

export function refineCampaignBrief(
  campaignId: string,
  payload: RefineBriefRequest
): Promise<RefineBriefResponse> {
  return apiPost<RefineBriefResponse>(`/campaigns/${campaignId}/refine-brief`, payload);
}

export function regenerateCampaignVariants(
  campaignId: string,
  payload: RegenerateVariantsRequest
): Promise<RegenerateVariantsResponse> {
  return apiPost<RegenerateVariantsResponse>(`/campaigns/${campaignId}/regenerate-variants`, payload);
}

export function listCampaignRefinements(campaignId: string): Promise<RefinementListResponse> {
  return apiGet<RefinementListResponse>(`/campaigns/${campaignId}/refinements`);
}

export function refineMessageVariant(
  variantId: string,
  payload: RefineVariantRequest
): Promise<RefineVariantResponse> {
  return apiPost<RefineVariantResponse>(`/variants/${variantId}/refine`, payload);
}
