from datetime import date

from app.tools.compliance_rules import RuleContext
from app.tools.guardrail_runner import run_guardrails


def test_guardrail_runner_scores_failed_for_high_risk_issue():
    result = run_guardrails(
        RuleContext(
            message_body="Last chance! Guaranteed savings with 50% discount. Hurry now!",
            channel="telegram",
            offer_details="25% discount",
        )
    )

    assert result.status == "FAILED"
    assert result.risk_level == "high"
    assert result.tool_executions


def test_guardrail_runner_scores_warning_for_medium_issue():
    result = run_guardrails(
        RuleContext(
            message_body="Get 25% discount today",
            channel="telegram",
            offer_details="25% discount",
            expiry_date=date(2026, 6, 30),
            cta_link="https://example.com/sale",
        )
    )

    assert result.status == "WARNING"
    assert result.risk_level == "medium"
