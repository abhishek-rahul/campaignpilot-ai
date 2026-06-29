import { apiPost } from './apiClient';
import type { ApprovalActionResponse, ApproveVariantRequest, RejectVariantRequest } from '../types/compliance';

export function approveVariant(variantId: string, payload: ApproveVariantRequest): Promise<ApprovalActionResponse> {
  return apiPost<ApprovalActionResponse>(`/variants/${variantId}/approve`, payload);
}

export function rejectVariant(variantId: string, payload: RejectVariantRequest): Promise<ApprovalActionResponse> {
  return apiPost<ApprovalActionResponse>(`/variants/${variantId}/reject`, payload);
}
