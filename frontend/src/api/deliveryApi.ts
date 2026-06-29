import { apiGet, apiPost } from './apiClient';
import type { DeliveryLog, DeliveryLogListResponse, SendPayloadResponse } from '../types/delivery';

export function sendPayload(payloadId: string): Promise<SendPayloadResponse> {
  return apiPost<SendPayloadResponse>(`/payloads/${payloadId}/send`);
}

export function listCampaignDeliveryLogs(campaignId: string): Promise<DeliveryLogListResponse> {
  return apiGet<DeliveryLogListResponse>(`/campaigns/${campaignId}/delivery-logs`);
}

export function getDeliveryLog(deliveryId: string): Promise<DeliveryLog> {
  return apiGet<DeliveryLog>(`/delivery-logs/${deliveryId}`);
}
