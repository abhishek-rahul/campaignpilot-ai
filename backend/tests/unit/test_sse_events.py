import json

from app.streaming.event_builder import error_event, final_event, start_event, token_event


def _data(frame: str) -> dict:
    line = next(item for item in frame.splitlines() if item.startswith("data: "))
    return json.loads(line.removeprefix("data: "))


def test_start_event_formats_sse_frame():
    frame = start_event(request_id="req_test", campaign_id="camp_1")

    assert frame.startswith("event: start\n")
    assert frame.endswith("\n\n")
    assert _data(frame)["campaign_id"] == "camp_1"


def test_token_event_formats_text_payload():
    frame = token_event("hello")

    assert "event: token" in frame
    assert _data(frame)["text"] == "hello"


def test_final_and_error_events_are_json_serialized():
    assert _data(final_event({"campaign_id": "camp_1"}))["campaign_id"] == "camp_1"
    assert _data(error_event(code="VALIDATION_ERROR", message="Bad input"))["code"] == "VALIDATION_ERROR"
