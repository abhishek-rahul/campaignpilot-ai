import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.llm import llm_client
from app.main import app


pytestmark = pytest.mark.integration


def _database_available() -> bool:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with engine.connect() as connection:
            connection.execute(text("select 1"))
            connection.execute(text("select 1 from evaluation_results limit 1"))
        return True
    except SQLAlchemyError:
        return False


@pytest.fixture(scope="module")
def client():
    if not _database_available():
        pytest.skip("Configured database/migration is not available; run docker compose and alembic.")
    return TestClient(app)


def _create_campaign_and_variant(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    monkeypatch.setattr(llm_client.settings, "openai_api_key", "replace_me")
    chat = client.post(
        "/api/v1/chat/campaign",
        json={
            "campaign_id": None,
            "message": (
                "Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. "
                "Channel should be Telegram. CTA is https://example.com/sale. Offer expires on 30 June."
            ),
            "stream": False,
        },
    )
    assert chat.status_code == 200
    campaign_id = chat.json()["data"]["campaign_id"]
    variants = client.post(
        f"/api/v1/campaigns/{campaign_id}/generate-variants",
        json={"variant_count": 3, "channels": ["telegram"], "use_rag_context": False},
    )
    assert variants.status_code == 200
    variant_id = variants.json()["data"]["variants"][0]["variant_id"]
    compliance = client.post(f"/api/v1/variants/{variant_id}/compliance-check", json={"use_rag_context": False})
    assert compliance.status_code == 200
    return campaign_id, variant_id


def test_slice_6_observability_and_evaluation_flow(client, monkeypatch):
    campaign_id, variant_id = _create_campaign_and_variant(client, monkeypatch)

    summary = client.get(f"/api/v1/campaigns/{campaign_id}/observability-summary")
    assert summary.status_code == 200
    assert summary.json()["data"]["llm_trace_count"] >= 2
    assert summary.json()["data"]["tool_call_count"] >= 1

    traces = client.get(f"/api/v1/campaigns/{campaign_id}/llm-traces")
    assert traces.status_code == 200
    trace_id = traces.json()["data"]["traces"][0]["trace_id"]
    trace_detail = client.get(f"/api/v1/llm-traces/{trace_id}")
    assert trace_detail.status_code == 200
    assert trace_detail.json()["data"]["prompt"] is not None

    tools = client.get(f"/api/v1/campaigns/{campaign_id}/tool-calls")
    assert tools.status_code == 200
    tool_call_id = tools.json()["data"]["tool_calls"][0]["tool_call_id"]
    tool_detail = client.get(f"/api/v1/tool-calls/{tool_call_id}")
    assert tool_detail.status_code == 200
    assert tool_detail.json()["data"]["input_json"] is not None

    evaluation = client.post(f"/api/v1/variants/{variant_id}/evaluate", json={"evaluation_type": "variant_quality"})
    assert evaluation.status_code == 200
    evaluation_id = evaluation.json()["data"]["evaluation_id"]
    assert evaluation.json()["data"]["variant_id"] == variant_id

    readiness = client.post(f"/api/v1/campaigns/{campaign_id}/evaluate-readiness")
    assert readiness.status_code == 200
    assert readiness.json()["data"]["evaluation_type"] == "campaign_readiness"

    evaluations = client.get(f"/api/v1/campaigns/{campaign_id}/evaluations")
    assert evaluations.status_code == 200
    assert len(evaluations.json()["data"]["evaluations"]) >= 2

    evaluation_detail = client.get(f"/api/v1/evaluations/{evaluation_id}")
    assert evaluation_detail.status_code == 200
    assert evaluation_detail.json()["data"]["checks"]

    timeline = client.get(f"/api/v1/campaigns/{campaign_id}/debug-timeline")
    assert timeline.status_code == 200
    events = timeline.json()["data"]["events"]
    assert events
    assert events == sorted(events, key=lambda event: (event["created_at"], event["event_id"]))


def test_slice_6_unknown_resources_return_not_found(client):
    assert client.get("/api/v1/campaigns/camp_missing/observability-summary").status_code == 404
    assert client.get("/api/v1/llm-traces/trace_missing").status_code == 404
    assert client.get("/api/v1/tool-calls/tool_missing").status_code == 404
    assert client.get("/api/v1/evaluations/evalres_missing").status_code == 404
    assert client.post("/api/v1/variants/var_missing/evaluate", json={"evaluation_type": "variant_quality"}).status_code == 404
