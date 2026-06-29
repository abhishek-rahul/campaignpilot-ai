export type ComplianceIssue = {
  rule_id: string;
  severity: string;
  message: string;
  evidence?: string | null;
};

export type CheckedRule = {
  rule_id: string;
  rule_name: string;
  passed: boolean;
  risk_level: string;
  issues_count: number;
};

export type ComplianceCheckRequest = {
  use_rag_context?: boolean;
  include_llm_explanation?: boolean;
};

export type ComplianceResult = {
  variant_id: string;
  campaign_id: string;
  compliance_result_id: string;
  status: string;
  risk_level: string;
  issues: ComplianceIssue[];
  checked_rules: CheckedRule[];
  recommendation: string;
  source_contexts_used: string[];
  created_at: string;
};

export type ComplianceResultListResponse = {
  variant_id: string;
  checks: ComplianceResult[];
};

export type ApproveVariantRequest = {
  reason?: string | null;
  allow_high_risk_override?: boolean;
};

export type RejectVariantRequest = {
  reason?: string | null;
};

export type ApprovalActionResponse = {
  variant_id: string;
  campaign_id: string;
  status: string;
  approval_action_id: string;
  previous_status: string;
  new_status: string;
  reason: string | null;
  override_used: boolean;
  created_at: string;
};

export type VariantComplianceSummaryItem = {
  variant_id: string;
  variant_name: string;
  channel: string;
  variant_status: string;
  risk_level: string | null;
  latest_compliance_status: string | null;
  latest_compliance_result_id: string | null;
  approval_status: string | null;
};

export type CampaignComplianceSummary = {
  campaign_id: string;
  variants_summary: VariantComplianceSummaryItem[];
  total_variants: number;
  passed_count: number;
  warning_count: number;
  failed_count: number;
  approved_count: number;
  rejected_count: number;
};
