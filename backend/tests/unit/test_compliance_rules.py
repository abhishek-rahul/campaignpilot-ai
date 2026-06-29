from datetime import date

from app.tools.compliance_rules import (
    RuleContext,
    aggressive_urgency_rule,
    cta_presence_rule,
    excessive_emoji_rule,
    expiry_clarity_rule,
    misleading_claim_rule,
    offer_consistency_rule,
)


def test_misleading_claim_rule_flags_forbidden_claim():
    result = misleading_claim_rule(RuleContext(message_body="Get guaranteed savings today", channel="telegram"))

    assert result.passed is False
    assert result.risk_level == "high"


def test_aggressive_urgency_rule_high_when_expiry_missing():
    result = aggressive_urgency_rule(RuleContext(message_body="Last chance, hurry now!", channel="telegram"))

    assert result.risk_level == "high"


def test_expiry_clarity_rule_warns_when_expiry_missing_from_copy():
    result = expiry_clarity_rule(
        RuleContext(message_body="Get 25% discount today", channel="telegram", expiry_date=date(2026, 6, 30))
    )

    assert result.passed is False
    assert result.risk_level == "medium"


def test_cta_presence_rule_passes_with_link():
    result = cta_presence_rule(
        RuleContext(message_body="Shop now: https://example.com/sale", channel="telegram", cta_link="https://example.com/sale")
    )

    assert result.passed is True


def test_offer_consistency_rule_flags_different_discount():
    result = offer_consistency_rule(
        RuleContext(message_body="Get 50% discount", channel="telegram", offer_details="25% discount")
    )

    assert result.passed is False
    assert result.risk_level == "high"


def test_excessive_emoji_rule_warns_after_threshold():
    result = excessive_emoji_rule(RuleContext(message_body="Sale 🔥🔥🔥🔥", channel="whatsapp_mock"))

    assert result.passed is False
    assert result.risk_level == "medium"
