import { apiGet } from './apiClient';
import type { DebugTimeline, LlmTraceList, ObservabilitySummary, ToolCallList } from '../types/observability';

export function getObservabilitySummary(campaignId: string): Promise<ObservabilitySummary> {
  return apiGet<ObservabilitySummary>(`/campaigns/${campaignId}/observability-summary`);
}

export function listLlmTraces(campaignId: string): Promise<LlmTraceList> {
  return apiGet<LlmTraceList>(`/campaigns/${campaignId}/llm-traces`);
}

export function listToolCalls(campaignId: string): Promise<ToolCallList> {
  return apiGet<ToolCallList>(`/campaigns/${campaignId}/tool-calls`);
}

export function getDebugTimeline(campaignId: string): Promise<DebugTimeline> {
  return apiGet<DebugTimeline>(`/campaigns/${campaignId}/debug-timeline`);
}
