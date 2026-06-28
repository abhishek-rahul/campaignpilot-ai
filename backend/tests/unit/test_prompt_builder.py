from app.llm.prompt_builder import build_brief_extraction_prompt, build_variant_generation_prompt


def test_brief_prompt_mentions_json_contract():
    prompt = build_brief_extraction_prompt("hello")
    assert "Return JSON only" in prompt
    assert "missing_fields" in prompt


def test_variant_prompt_excludes_future_slice_features():
    prompt = build_variant_generation_prompt(
        campaign_name="Test",
        goal="Goal",
        target_audience="Audience",
        offer_details="Offer",
        tone="friendly",
        preferred_channels=["telegram"],
        cta_link="https://example.com",
        expiry_date=None,
        variant_count=3,
    )
    assert "Do not use RAG" in prompt
    assert "telegram" in prompt
