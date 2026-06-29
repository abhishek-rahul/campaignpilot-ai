from __future__ import annotations

import re
from typing import Any

from app.evaluation.scoring import grade_for_score, passed_for_checks
from app.schemas.evaluation_schema import EvaluationCheckData

CTA_WORDS = ("shop now", "claim", "learn more", "tap", "start here")
AGGRESSIVE_PHRASES = ("last chance", "final warning", "hurry now")
HIGH_RISK_PHRASES = ("guaranteed savings", "100% guaranteed", "risk free", "no terms apply")


def evaluate_variant_quality(*, variant: Any, brief: Any | None) -> dict[str, Any]:
    body = variant.message_body or ""
    lower = body.lower()
    checks = [
        _has_cta(lower, brief),
        _length_fit(body, variant.channel),
        _tone_alignment(variant, brief),
        _offer_present(lower, brief),
        _not_too_aggressive(lower),
        _compliance_safe_hint(lower),
    ]
    score = sum(check.score for check in checks)
    grade = grade_for_score(score)
    passed = passed_for_checks(score, checks)
    return {
        "score": score,
        "grade": grade,
        "passed": passed,
        "checks": checks,
        "recommendation": _recommendation(checks, passed),
    }


def _has_cta(lower_body: str, brief: Any | None) -> EvaluationCheckData:
    cta_link = (getattr(brief, "cta_link", None) or "").lower()
    passed = bool(cta_link and cta_link in lower_body) or any(word in lower_body for word in CTA_WORDS)
    return _check("has_cta", passed, 20, "CTA is present" if passed else "Add a CTA link or clear CTA wording.")


def _length_fit(body: str, channel: str) -> EvaluationCheckData:
    limit = 500 if channel == "whatsapp_mock" else 280
    passed = len(body) <= limit
    return _check("length_fit", passed, 20, f"Message length is within {limit} characters." if passed else f"Shorten copy to {limit} characters or less.")


def _tone_alignment(variant: Any, brief: Any | None) -> EvaluationCheckData:
    brief_tone = (getattr(brief, "tone", None) or "").lower()
    variant_tone = (getattr(variant, "tone", None) or "").lower()
    passed = not brief_tone or not variant_tone or brief_tone == variant_tone
    return _check("tone_alignment", passed, 15, "Variant tone aligns with the brief." if passed else "Align variant tone with the campaign brief.")


def _offer_present(lower_body: str, brief: Any | None) -> EvaluationCheckData:
    offer = (getattr(brief, "offer_details", None) or "").lower()
    percentages = re.findall(r"\d+%", offer)
    passed = bool(offer and offer in lower_body) or any(percent in lower_body for percent in percentages)
    return _check("offer_present", passed, 20, "Offer details are present." if passed else "Mention the offer or discount clearly.")


def _not_too_aggressive(lower_body: str) -> EvaluationCheckData:
    failed_phrase = next((phrase for phrase in AGGRESSIVE_PHRASES if phrase in lower_body), None)
    return _check(
        "not_too_aggressive",
        failed_phrase is None,
        15,
        "No aggressive urgency found." if failed_phrase is None else f"Remove aggressive urgency phrase: {failed_phrase}.",
        high_risk=failed_phrase is not None,
    )


def _compliance_safe_hint(lower_body: str) -> EvaluationCheckData:
    failed_phrase = next((phrase for phrase in HIGH_RISK_PHRASES if phrase in lower_body), None)
    return _check(
        "compliance_safe_hint",
        failed_phrase is None,
        10,
        "No high-risk claim hints found." if failed_phrase is None else f"Remove high-risk claim: {failed_phrase}.",
        high_risk=failed_phrase is not None,
    )


def _check(check_id: str, passed: bool, max_score: int, message: str, *, high_risk: bool = False) -> EvaluationCheckData:
    return EvaluationCheckData(
        check_id=check_id,
        passed=passed,
        score=max_score if passed else 0,
        max_score=max_score,
        message=message,
        high_risk=high_risk,
    )


def _recommendation(checks: list[EvaluationCheckData], passed: bool) -> str:
    if passed:
        return "Variant quality looks good for human review."
    failed = [check.message for check in checks if not check.passed]
    return "Improve before relying on this variant: " + " ".join(failed)
