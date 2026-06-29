from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any

from app.tools.compliance_rules import ALL_RULES, RuleContext, RuleIssue, RuleResult


@dataclass(frozen=True)
class ToolExecution:
    tool_name: str
    input_json: dict[str, Any]
    output_json: dict[str, Any]
    status: str
    latency_ms: int
    error_message: str | None = None


@dataclass(frozen=True)
class GuardrailRunResult:
    status: str
    risk_level: str
    issues: list[RuleIssue]
    checked_rules: list[RuleResult]
    recommendation: str
    tool_executions: list[ToolExecution]


def run_guardrails(context: RuleContext) -> GuardrailRunResult:
    checked_rules: list[RuleResult] = []
    executions: list[ToolExecution] = []
    for rule in ALL_RULES:
        started = time.perf_counter()
        input_json = {
            "message_body": context.message_body,
            "channel": context.channel,
            "cta_link": context.cta_link,
            "expiry_date": context.expiry_date.isoformat() if context.expiry_date else None,
            "offer_details": context.offer_details,
            "context_count": len(context.retrieved_contexts),
        }
        try:
            result = rule(context)
            checked_rules.append(result)
            executions.append(
                ToolExecution(
                    tool_name=result.rule_id,
                    input_json=input_json,
                    output_json=_rule_to_json(result),
                    status="SUCCESS",
                    latency_ms=int((time.perf_counter() - started) * 1000),
                )
            )
        except Exception as exc:  # noqa: BLE001
            executions.append(
                ToolExecution(
                    tool_name=getattr(rule, "__name__", "unknown_rule"),
                    input_json=input_json,
                    output_json={},
                    status="FAILED",
                    latency_ms=int((time.perf_counter() - started) * 1000),
                    error_message=str(exc),
                )
            )
    issues = [issue for result in checked_rules for issue in result.issues]
    status, risk_level, recommendation = _score(issues)
    return GuardrailRunResult(status, risk_level, issues, checked_rules, recommendation, executions)


def result_to_json(result: GuardrailRunResult) -> dict[str, Any]:
    return {
        "status": result.status,
        "risk_level": result.risk_level,
        "issues": [asdict(issue) for issue in result.issues],
        "checked_rules": [_rule_to_json(rule) for rule in result.checked_rules],
        "recommendation": result.recommendation,
    }


def _score(issues: list[RuleIssue]) -> tuple[str, str, str]:
    if any(issue.severity == "high" for issue in issues):
        return "FAILED", "high", "Do not approve until high-risk claims are removed"
    if any(issue.severity == "medium" for issue in issues):
        return "WARNING", "medium", "Needs copy edit before approval"
    return "PASSED", "low", "Approved for review"


def _rule_to_json(result: RuleResult) -> dict[str, Any]:
    return {
        "rule_id": result.rule_id,
        "rule_name": result.rule_name,
        "passed": result.passed,
        "risk_level": result.risk_level,
        "issues_count": len(result.issues),
        "issues": [asdict(issue) for issue in result.issues],
    }
