from app.llm import llm_client


def test_mock_brief_extracts_manual_prompt():
    result = llm_client.extract_campaign_brief(
        "Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. "
        "Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June."
    )
    assert result.used_mock is True
    assert result.data["brief_status"] == "COMPLETE"
    assert result.data["preferred_channels"] == ["telegram", "whatsapp_mock"]
    assert result.data["cta_link"] == "https://example.com/sale"


def test_mock_variant_generation_returns_requested_count():
    result = llm_client.generate_message_variants(
        campaign_name="Festive Reactivation Campaign",
        goal="Reactivate inactive customers",
        target_audience="inactive customers",
        offer_details="25% discount",
        tone="friendly",
        preferred_channels=["telegram", "whatsapp_mock"],
        cta_link="https://example.com/sale",
        expiry_date="2026-06-30",
        variant_count=3,
    )
    assert result.used_mock is True
    assert len(result.data["variants"]) == 3
    assert {variant["channel"] for variant in result.data["variants"]} == {"telegram", "whatsapp_mock"}
