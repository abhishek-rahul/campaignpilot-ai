from app.llm.prompt_builder import build_brief_refinement_prompt, build_variant_refinement_prompt


def test_brief_refinement_prompt_contains_current_brief_and_feedback():
    prompt = build_brief_refinement_prompt(
        current_brief={"goal": "Reactivate customers", "tone": "friendly"},
        feedback="Make it premium",
        rag_context=[{"text": "Avoid aggressive urgency"}],
    )

    assert "Reactivate customers" in prompt
    assert "Make it premium" in prompt
    assert "Avoid aggressive urgency" in prompt


def test_variant_refinement_prompt_contains_source_variant_and_feedback():
    prompt = build_variant_refinement_prompt(
        current_brief={"offer_details": "25% discount"},
        source_variant={"message_body": "Shop now", "channel": "telegram"},
        feedback="Make it shorter",
    )

    assert "25% discount" in prompt
    assert "Shop now" in prompt
    assert "Make it shorter" in prompt
