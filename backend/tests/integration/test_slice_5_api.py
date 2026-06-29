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
            connection.execute(text("select 1 from campaign_refinements limit 1"))
        return True
    except SQLAlchemyError:
        return False


@pytest.fixture(scope="module")
def client():
    if not _database_available():
        pytest.skip("Configured database/migration is not available; run docker compose and alembic.")
    return TestClient(app)


def _create_campaign(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setattr(llm_client.settings, "openai_api_key", "replace_me")
    response = client.post(
        "/api/v1/chat/campaign",
        json={
            "campaign_id": None,
            "message": (
                "Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. "
                "Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June."
            ),
            "stream": False,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["campaign_id"]


def _generate_variant(client: TestClient, campaign_id: str) -> str:
    response = client.post(
        f"/api/v1/campaigns/{campaign_id}/generate-variants",
        json={"variant_count": 3, "channels": ["telegram"], "use_rag_context": False},
    )
    assert response.status_code == 200
    return response.json()["data"]["variants"][0]["variant_id"]


def test_streaming_chat_returns_start_token_and_final(client, monkeypatch):
    monkeypatch.setattr(llm_client.settings, "openai_api_key", "replace_me")

    with client.stream(
        "POST",
        "/api/v1/chat/campaign/stream",
        json={
            "campaign_id": None,
            "message": (
                "Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. "
                "Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. Offer expires on 30 June."
            ),
            "stream": True,
        },
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert "event: start" in body
    assert "event: token" in body
    assert "event: final" in body
    assert "campaign_brief" in body


def test_refinement_loop_endpoints(client, monkeypatch):
    campaign_id = _create_campaign(client, monkeypatch)
    variant_id = _generate_variant(client, campaign_id)

    proposal_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/refine-brief",
        json={"feedback": "Make it premium", "use_rag_context": False, "apply": False},
    )
    assert proposal_response.status_code == 200
    assert proposal_response.json()["data"]["applied"] is False

    apply_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/refine-brief",
        json={"feedback": "Make it premium and less pushy", "use_rag_context": False, "apply": True},
    )
    assert apply_response.status_code == 200
    assert apply_response.json()["data"]["after_brief"]["tone"] == "premium"

    refine_variant_response = client.post(
        f"/api/v1/variants/{variant_id}/refine",
        json={"feedback": "Make it shorter", "use_rag_context": False, "create_new_variant": True},
    )
    assert refine_variant_response.status_code == 200
    assert refine_variant_response.json()["data"]["source_variant_id"] == variant_id
    assert refine_variant_response.json()["data"]["refined_variant"]["status"] == "GENERATED"

    regenerate_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/regenerate-variants",
        json={"feedback": "Make all variants softer", "variant_count": 3, "channels": ["telegram"], "use_rag_context": False},
    )
    assert regenerate_response.status_code == 200
    assert len(regenerate_response.json()["data"]["variants"]) == 3

    history_response = client.get(f"/api/v1/campaigns/{campaign_id}/refinements")
    assert history_response.status_code == 200
    assert len(history_response.json()["data"]["refinements"]) >= 4
