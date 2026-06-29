from types import SimpleNamespace

from app.evaluation.scoring import grade_for_score
from app.evaluation.variant_quality import evaluate_variant_quality


def test_variant_quality_scores_strong_copy():
    variant = SimpleNamespace(
        message_body="Hi! Get 25% discount before 2026-06-30. Shop now: https://example.com/sale",
        channel="telegram",
        tone="friendly",
    )
    brief = SimpleNamespace(tone="friendly", offer_details="25% discount", cta_link="https://example.com/sale")

    result = evaluate_variant_quality(variant=variant, brief=brief)

    assert result["score"] == 100
    assert result["grade"] == "A"
    assert result["passed"] is True


def test_high_risk_phrase_fails_even_with_good_score():
    variant = SimpleNamespace(
        message_body="Claim 25% discount with guaranteed savings at https://example.com/sale",
        channel="telegram",
        tone="friendly",
    )
    brief = SimpleNamespace(tone="friendly", offer_details="25% discount", cta_link="https://example.com/sale")

    result = evaluate_variant_quality(variant=variant, brief=brief)

    assert result["passed"] is False
    assert any(check.check_id == "compliance_safe_hint" and check.high_risk for check in result["checks"])


def test_grade_boundaries():
    assert grade_for_score(85) == "A"
    assert grade_for_score(70) == "B"
    assert grade_for_score(50) == "C"
    assert grade_for_score(49) == "D"
