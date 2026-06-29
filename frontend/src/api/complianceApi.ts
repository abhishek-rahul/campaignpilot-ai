import { apiGet, apiPost } from './apiClient';
import type { ComplianceCheckRequest, ComplianceResult, ComplianceResultListResponse } from '../types/compliance';

export function runVariantComplianceCheck(
  variantId: string,
  payload: ComplianceCheckRequest = {}
): Promise<ComplianceResult> {
  return apiPost<ComplianceResult>(`/variants/${variantId}/compliance-check`, payload);
}

export function listVariantComplianceChecks(variantId: string): Promise<ComplianceResultListResponse> {
  return apiGet<ComplianceResultListResponse>(`/variants/${variantId}/compliance-checks`);
}
