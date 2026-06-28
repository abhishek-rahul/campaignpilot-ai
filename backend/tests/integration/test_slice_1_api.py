import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.main import app


pytestmark = pytest.mark.integration


def _database_available() -> bool:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        return True
    except SQLAlchemyError:
        return False


@pytest.fixture(scope="module")
def client():
    if not _database_available():
        pytest.skip("Configured database is not available; run docker compose and alembic for integration tests.")
    return TestClient(app)


def test_slice_1_chat_campaign_variant_flow(client):
    chat_response = client.post(
        "/api/v1/chat/campaign",
        json={
            "campaign_id": None,
            "message": (
                "Create a festive campaign for inactive customers with 25% discount. Tone should be friendly. "
                "Channel should be Telegram and WhatsApp mock. CTA is https://example.com/sale. "
                "Offer expires on 30 June."
            ),
            "stream": False,
        },
    )
    assert chat_response.status_code == 200
    chat_body = chat_response.json()
    assert chat_body["success"] is True
    campaign_id = chat_body["data"]["campaign_id"]
    assert chat_body["data"]["brief_status"] == "COMPLETE"

    get_response = client.get(f"/api/v1/campaigns/{campaign_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["status"] == "BRIEF_EXTRACTED"

    conversation_response = client.get(f"/api/v1/campaigns/{campaign_id}/conversation")
    assert conversation_response.status_code == 200
    assert len(conversation_response.json()["data"]["messages"]) == 2

    variants_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/generate-variants",
        json={"variant_count": 3, "channels": ["telegram", "whatsapp_mock"], "use_rag_context": False, "use_memory": False},
    )
    assert variants_response.status_code == 200
    variants = variants_response.json()["data"]["variants"]
    assert len(variants) == 3

    list_response = client.get(f"/api/v1/campaigns/{campaign_id}/variants")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]["variants"]) >= 3

    variant_id = variants[0]["variant_id"]
    update_response = client.patch(f"/api/v1/variants/{variant_id}", json={"tone": "friendly", "message_body": "Updated body"})
    assert update_response.status_code == 200
    assert set(update_response.json()["data"]["updated_fields"]) == {"tone", "message_body"}


def test_chat_missing_message_validation(client):
    response = client.post("/api/v1/chat/campaign", json={"campaign_id": None, "message": "", "stream": False})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
