from types import SimpleNamespace

from app.llm import llm_client
from app.services import refinement_service


def test_mock_brief_refinement_updates_premium_tone(monkeypatch):
    monkeypatch.setattr(llm_client.settings, "openai_api_key", "replace_me")

    result = llm_client.refine_campaign_brief(
        current_brief={
            "goal": "Reactivate customers",
            "target_audience": "inactive customers",
            "offer_details": "25% discount",
            "tone": "friendly",
            "preferred_channels": ["telegram"],
            "cta_link": "https://example.com/sale",
            "expiry_date": "2026-06-30",
        },
        feedback="Make it premium",
    )

    assert result.used_mock is True
    assert result.data["tone"] == "premium"


def test_safe_reset_clears_selected_variant_after_approval():
    campaign = SimpleNamespace(status="APPROVED", selected_variant_id="var_1")

    refinement_service._apply_safe_reset(campaign)

    assert campaign.status == "NEEDS_REVIEW"
    assert campaign.selected_variant_id is None
