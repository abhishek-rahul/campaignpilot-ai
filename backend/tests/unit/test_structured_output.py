from app.llm.structured_output import normalize_brief, parse_json_object


def test_parse_json_object_handles_code_fence():
    parsed = parse_json_object('```json\n{"ok": true}\n```')
    assert parsed == {"ok": True}


def test_normalize_brief_detects_missing_fields():
    brief = normalize_brief({"goal": "Reactivate customers", "preferred_channels": ["Telegram"]})
    assert brief["preferred_channels"] == ["telegram"]
    assert brief["brief_status"] == "INCOMPLETE"
    assert "cta_link" in brief["missing_fields"]
