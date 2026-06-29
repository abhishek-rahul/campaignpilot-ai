from datetime import datetime, timezone
from types import SimpleNamespace

from app.services import observability_service


def test_llm_trace_preview_truncates_prompt_and_response():
    trace = SimpleNamespace(
        id="trace_1",
        operation_name="variant_generation",
        model_name="mock-llm",
        trace_metadata={"used_mock": True},
        latency_ms=12,
        status="SUCCESS",
        prompt="word " * 100,
        response="answer " * 100,
        error_message=None,
        created_at=datetime.now(timezone.utc),
    )

    preview = observability_service._trace_preview(trace)

    assert preview.used_mock is True
    assert preview.prompt_preview is not None
    assert len(preview.prompt_preview) <= 180
    assert preview.prompt_preview.endswith("...")


def test_debug_timeline_sorts_events():
    older = SimpleNamespace(id="msg_1", sender="CAMPAIGN_MANAGER", message_text="hello", created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    newer = SimpleNamespace(id="msg_2", sender="AI_AGENT", message_text="hi", created_at=datetime(2026, 1, 2, tzinfo=timezone.utc))

    first = observability_service._timeline_event("conversation_message", newer)
    second = observability_service._timeline_event("conversation_message", older)
    events = sorted([first, second], key=lambda event: (event.created_at, event.event_id))

    assert events[0].related_id == "msg_1"
