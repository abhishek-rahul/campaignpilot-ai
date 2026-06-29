export type ObservabilitySummary = {
  campaign_id: string;
  llm_trace_count: number;
  retrieved_context_count: number;
  compliance_result_count: number;
  tool_call_count: number;
  payload_count: number;
  delivery_log_count: number;
  refinement_count: number;
  evaluation_count: number;
  latest_llm_trace_at: string | null;
  latest_tool_call_at: string | null;
  latest_delivery_at: string | null;
  latest_refinement_at: string | null;
  latest_evaluation_at: string | null;
};

export type LlmTracePreview = {
  trace_id: string;
  operation_name: string;
  model_name: string;
  used_mock: boolean;
  latency_ms: number | null;
  status: string;
  prompt_preview: string | null;
  response_preview: string | null;
  error_message: string | null;
  created_at: string;
};

export type LlmTraceList = {
  campaign_id: string;
  traces: LlmTracePreview[];
};

export type ToolCallPreview = {
  tool_call_id: string;
  tool_name: string;
  status: string;
  latency_ms: number | null;
  error_message: string | null;
  created_at: string;
};

export type ToolCallList = {
  campaign_id: string;
  tool_calls: ToolCallPreview[];
};

export type DebugTimelineEvent = {
  event_id: string;
  event_type: string;
  title: string;
  summary: string;
  created_at: string;
  related_id: string | null;
};

export type DebugTimeline = {
  campaign_id: string;
  events: DebugTimelineEvent[];
};
