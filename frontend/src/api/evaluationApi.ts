import { apiGet, apiPost } from './apiClient';
import type { EvaluationList, EvaluationResult } from '../types/evaluation';

export function runVariantEvaluation(variantId: string): Promise<EvaluationResult> {
  return apiPost<EvaluationResult>(`/variants/${variantId}/evaluate`, { evaluation_type: 'variant_quality' });
}

export function runCampaignReadinessEvaluation(campaignId: string): Promise<EvaluationResult> {
  return apiPost<EvaluationResult>(`/campaigns/${campaignId}/evaluate-readiness`);
}

export function listCampaignEvaluations(campaignId: string): Promise<EvaluationList> {
  return apiGet<EvaluationList>(`/campaigns/${campaignId}/evaluations`);
}
