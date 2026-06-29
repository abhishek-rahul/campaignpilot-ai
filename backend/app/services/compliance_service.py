from __future__ import annotations

from dataclasses import asdict

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, compliance_repository, rag_repository, tool_call_repository, variant_repository
from app.schemas.compliance_schema import (
    CheckedRule,
    ComplianceCheckRequest,
    ComplianceIssue,
    ComplianceResultData,
    ComplianceResultListData,
)
from app.tools.compliance_rules import RuleContext
from app.tools.guardrail_runner import result_to_json, run_guardrails


def run_compliance_check(db: Session, variant_id: str, request: ComplianceCheckRequest) -> ComplianceResultData:
    variant = variant_repository.get_variant(db, variant_id)
    if variant is None:
        raise ResourceNotFoundError("Variant not found")
    campaign = campaign_repository.get_campaign(db, variant.campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    brief = campaign_repository.get_brief_for_campaign(db, campaign.id)
    contexts = []
    if request.use_rag_context:
        contexts = rag_repository.list_retrieved_contexts(db, campaign.id, limit=5)
    context_payload = [
        {
            "context_id": context.id,
            "retrieved_text": context.retrieved_text,
            "score": context.score,
            "rank_position": context.rank_position,
        }
        for context in contexts
    ]
    rule_context = RuleContext(
        message_body=variant.message_body,
        channel=variant.channel,
        cta_link=brief.cta_link if brief else None,
        expiry_date=brief.expiry_date if brief else None,
        offer_details=brief.offer_details if brief else None,
        retrieved_contexts=context_payload,
    )
    result = run_guardrails(rule_context)
    source_context_ids = [context.id for context in contexts]
    row = compliance_repository.create_compliance_result(
        db,
        {
            "id": new_id("comp"),
            "campaign_id": campaign.id,
            "variant_id": variant.id,
            "status": result.status,
            "risk_level": result.risk_level,
            "issues_json": [asdict(issue) for issue in result.issues],
            "checked_rules_json": [
                {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "passed": rule.passed,
                    "risk_level": rule.risk_level,
                    "issues_count": len(rule.issues),
                }
                for rule in result.checked_rules
            ],
            "recommendation": result.recommendation,
            "source_context_ids_json": source_context_ids,
            "raw_result_json": result_to_json(result),
        },
    )
    for execution in result.tool_executions:
        tool_call_repository.create_tool_call_log(
            db,
            {
                "id": new_id("tool"),
                "campaign_id": campaign.id,
                "variant_id": variant.id,
                "tool_name": execution.tool_name,
                "input_json": execution.input_json,
                "output_json": execution.output_json,
                "status": execution.status,
                "latency_ms": execution.latency_ms,
                "error_message": execution.error_message,
            },
        )
    variant_status = "COMPLIANCE_FAILED" if result.status == "FAILED" else "COMPLIANCE_PASSED"
    variant_repository.update_variant_risk_and_status(db, variant, risk_level=result.risk_level, status=variant_status)
    campaign_repository.update_campaign_status(db, campaign, "NEEDS_REVIEW" if result.status == "FAILED" else "COMPLIANCE_CHECKED")
    db.commit()
    db.refresh(row)
    return _result_data(row)


def list_compliance_checks(db: Session, variant_id: str) -> ComplianceResultListData:
    if variant_repository.get_variant(db, variant_id) is None:
        raise ResourceNotFoundError("Variant not found")
    return ComplianceResultListData(
        variant_id=variant_id,
        checks=[_result_data(row) for row in compliance_repository.list_compliance_results(db, variant_id)],
    )


def _result_data(row) -> ComplianceResultData:
    return ComplianceResultData(
        variant_id=row.variant_id,
        campaign_id=row.campaign_id,
        compliance_result_id=row.id,
        status=row.status,
        risk_level=row.risk_level,
        issues=[ComplianceIssue(**issue) for issue in row.issues_json],
        checked_rules=[
            CheckedRule(
                rule_id=rule["rule_id"],
                rule_name=rule["rule_name"],
                passed=rule["passed"],
                risk_level=rule["risk_level"],
                issues_count=rule.get("issues_count", 0),
            )
            for rule in row.checked_rules_json
        ],
        recommendation=row.recommendation,
        source_contexts_used=row.source_context_ids_json or [],
        created_at=row.created_at,
    )
