from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class RuleContext:
    message_body: str
    channel: str
    cta_link: str | None = None
    expiry_date: date | None = None
    offer_details: str | None = None
    retrieved_contexts: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class RuleIssue:
    rule_id: str
    severity: str
    message: str
    evidence: str | None = None


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    rule_name: str
    passed: bool
    risk_level: str
    issues: list[RuleIssue] = field(default_factory=list)


FORBIDDEN_CLAIMS = ["guaranteed savings", "guaranteed results", "100% guaranteed", "risk free", "no terms apply"]
URGENCY_PHRASES = ["last chance", "act now", "hurry now", "only today", "final warning"]
CTA_WORDS = ["shop now", "tap here", "click", "claim", "start here", "buy now", "learn more"]


def misleading_claim_rule(context: RuleContext) -> RuleResult:
    found = _find_phrases(context.message_body, FORBIDDEN_CLAIMS)
    issues = [
        RuleIssue(
            rule_id="misleading_claim",
            severity="high",
            message="Remove misleading or absolute claim before approval.",
            evidence=phrase,
        )
        for phrase in found
    ]
    return RuleResult("misleading_claim", "Forbidden misleading claims", not issues, "high" if issues else "low", issues)


def aggressive_urgency_rule(context: RuleContext) -> RuleResult:
    found = _find_phrases(context.message_body, URGENCY_PHRASES)
    if not found:
        return RuleResult("aggressive_urgency", "Aggressive urgency", True, "low", [])
    severity = "high" if context.expiry_date is None else "medium"
    issues = [
        RuleIssue(
            rule_id="aggressive_urgency",
            severity=severity,
            message="Urgency wording should match the real campaign expiry.",
            evidence=phrase,
        )
        for phrase in found
    ]
    return RuleResult("aggressive_urgency", "Aggressive urgency", False, severity, issues)


def expiry_clarity_rule(context: RuleContext) -> RuleResult:
    if context.expiry_date is None:
        return RuleResult("expiry_clarity", "Expiry clarity", True, "low", [])
    body = context.message_body.lower()
    expiry_tokens = [
        str(context.expiry_date.day),
        context.expiry_date.strftime("%d"),
        context.expiry_date.strftime("%B").lower(),
        context.expiry_date.strftime("%b").lower(),
        str(context.expiry_date.year),
        "expires",
        "expiry",
        "before",
        "until",
    ]
    if any(token in body for token in expiry_tokens):
        return RuleResult("expiry_clarity", "Expiry clarity", True, "low", [])
    issue = RuleIssue("expiry_clarity", "medium", "Mention the offer expiry or time limit.", None)
    return RuleResult("expiry_clarity", "Expiry clarity", False, "medium", [issue])


def cta_presence_rule(context: RuleContext) -> RuleResult:
    body = context.message_body.lower()
    if context.cta_link and context.cta_link.lower() in body:
        return RuleResult("cta_presence", "CTA presence", True, "low", [])
    if any(word in body for word in CTA_WORDS):
        return RuleResult("cta_presence", "CTA presence", True, "low", [])
    issue = RuleIssue("cta_presence", "medium", "Add a clear CTA or link.", None)
    return RuleResult("cta_presence", "CTA presence", False, "medium", [issue])


def offer_consistency_rule(context: RuleContext) -> RuleResult:
    expected = _extract_discount(context.offer_details or "")
    claimed = _extract_discount(context.message_body)
    if expected is None or claimed is None or expected == claimed:
        return RuleResult("offer_consistency", "Offer consistency", True, "low", [])
    issue = RuleIssue(
        "offer_consistency",
        "high",
        f"Variant claims {claimed}% discount but brief says {expected}%.",
        f"{claimed}% discount",
    )
    return RuleResult("offer_consistency", "Offer consistency", False, "high", [issue])


def excessive_emoji_rule(context: RuleContext) -> RuleResult:
    count = sum(1 for char in context.message_body if ord(char) >= 0x1F300)
    if count <= 3:
        return RuleResult("excessive_emoji", "Excessive emoji", True, "low", [])
    issue = RuleIssue("excessive_emoji", "medium", "Reduce emoji usage to keep copy professional.", str(count))
    return RuleResult("excessive_emoji", "Excessive emoji", False, "medium", [issue])


def channel_fit_rule(context: RuleContext) -> RuleResult:
    if context.channel == "telegram" and len(context.message_body) > 280:
        issue = RuleIssue("channel_fit", "medium", "Telegram copy should stay short and scannable.", str(len(context.message_body)))
        return RuleResult("channel_fit", "Channel fit", False, "medium", [issue])
    return RuleResult("channel_fit", "Channel fit", True, "low", [])


def brand_context_rule(context: RuleContext) -> RuleResult:
    context_text = " ".join((item.get("retrieved_text") or item.get("text") or "") for item in context.retrieved_contexts).lower()
    if not context_text:
        return RuleResult("brand_context", "Brand guideline context awareness", True, "low", [])
    issues: list[RuleIssue] = []
    body = context.message_body.lower()
    if "avoid aggressive urgency" in context_text and _find_phrases(body, URGENCY_PHRASES):
        issues.append(RuleIssue("brand_context", "medium", "Uploaded guidelines discourage aggressive urgency.", "avoid aggressive urgency"))
    if "do not claim guaranteed savings" in context_text and "guaranteed savings" in body:
        issues.append(RuleIssue("brand_context", "high", "Uploaded guidelines prohibit guaranteed savings claims.", "guaranteed savings"))
    if "mention offer expiry clearly" in context_text and context.expiry_date and not expiry_clarity_rule(context).passed:
        issues.append(RuleIssue("brand_context", "medium", "Uploaded guidelines ask to mention expiry clearly.", "mention offer expiry clearly"))
    risk = "high" if any(issue.severity == "high" for issue in issues) else ("medium" if issues else "low")
    return RuleResult("brand_context", "Brand guideline context awareness", not issues, risk, issues)


ALL_RULES = [
    misleading_claim_rule,
    aggressive_urgency_rule,
    expiry_clarity_rule,
    cta_presence_rule,
    offer_consistency_rule,
    excessive_emoji_rule,
    channel_fit_rule,
    brand_context_rule,
]


def _find_phrases(text: str, phrases: list[str]) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if phrase in lower]


def _extract_discount(text: str) -> int | None:
    match = re.search(r"(\d{1,3})\s*%", text)
    return int(match.group(1)) if match else None
