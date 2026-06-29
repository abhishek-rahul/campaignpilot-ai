from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ComplianceCheckRequest(BaseModel):
    use_rag_context: bool = True
    include_llm_explanation: bool = False


class ComplianceIssue(BaseModel):
    rule_id: str
    severity: str
    message: str
    evidence: str | None = None


class CheckedRule(BaseModel):
    rule_id: str
    rule_name: str
    passed: bool
    risk_level: str
    issues_count: int = 0


class ComplianceResultData(BaseModel):
    variant_id: str
    campaign_id: str
    compliance_result_id: str
    status: str
    risk_level: str
    issues: list[ComplianceIssue] = Field(default_factory=list)
    checked_rules: list[CheckedRule] = Field(default_factory=list)
    recommendation: str
    source_contexts_used: list[str] = Field(default_factory=list)
    created_at: datetime


class ComplianceResultListData(BaseModel):
    variant_id: str
    checks: list[ComplianceResultData]


class VariantComplianceSummaryItem(BaseModel):
    variant_id: str
    variant_name: str
    channel: str
    variant_status: str
    risk_level: str | None = None
    latest_compliance_status: str | None = None
    latest_compliance_result_id: str | None = None
    approval_status: str | None = None


class CampaignComplianceSummaryData(BaseModel):
    campaign_id: str
    variants_summary: list[VariantComplianceSummaryItem]
    total_variants: int
    passed_count: int
    warning_count: int
    failed_count: int
    approved_count: int
    rejected_count: int
