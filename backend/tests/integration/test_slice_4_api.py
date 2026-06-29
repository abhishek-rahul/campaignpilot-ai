import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.channels.base_channel import SendResult
from app.channels.channel_registry import channel_registry
from app.core.config import settings
from app.llm import llm_client
from app.main import app


pytestmark = pytest.mark.integration


def _database_available() -> bool:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with engine.connect() as connection:
            connection.execute(text("select 1"))
            connection.execute(text("select 1 from channel_payloads limit 1"))
            connection.execute(text("select 1 from delivery_logs limit 1"))
        return True
    except SQLAlchemyError:
        return False


@pytest.fixture(scope="module")
def client():
    if not _database_available():
        pytest.skip("Configured database/migration is not available; run docker compose and alembic.")
    return TestClient(app)


def _create_campaign_and_variants(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> tuple[str, list[dict]]:
    monkeypatch.setattr(llm_client.settings, "openai_api_key", "replace_me")
    chat_response = client.post(
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
    assert chat_response.status_code == 200
    campaign_id = chat_response.json()["data"]["campaign_id"]
    variants_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/generate-variants",
        json={"variant_count": 3, "channels": ["telegram", "whatsapp_mock"], "use_rag_context": False},
    )
    assert variants_response.status_code == 200
    return campaign_id, variants_response.json()["data"]["variants"]


def _approve_variant(client: TestClient, variant_id: str) -> None:
    check_response = client.post(f"/api/v1/variants/{variant_id}/compliance-check", json={"use_rag_context": False})
    assert check_response.status_code == 200
    approve_response = client.post(f"/api/v1/variants/{variant_id}/approve", json={"reason": "Looks good"})
    assert approve_response.status_code == 200


def test_slice_4_full_payload_and_mocked_telegram_send(client, monkeypatch):
    campaign_id, variants = _create_campaign_and_variants(client, monkeypatch)
    variant_id = variants[0]["variant_id"]
    _approve_variant(client, variant_id)

    readiness_response = client.get(f"/api/v1/campaigns/{campaign_id}/payload-readiness")
    assert readiness_response.status_code == 200
    assert readiness_response.json()["data"]["ready"] is True

    payload_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/payloads",
        json={"channels": ["telegram", "whatsapp_mock"], "regenerate": False},
    )
    assert payload_response.status_code == 200
    payloads = payload_response.json()["data"]["payloads"]
    assert {payload["channel"] for payload in payloads} == {"telegram", "whatsapp_mock"}
    telegram_payload_id = next(payload["payload_id"] for payload in payloads if payload["channel"] == "telegram")
    whatsapp_payload_id = next(payload["payload_id"] for payload in payloads if payload["channel"] == "whatsapp_mock")

    list_response = client.get(f"/api/v1/campaigns/{campaign_id}/payloads")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]["payloads"]) >= 2

    detail_response = client.get(f"/api/v1/payloads/{telegram_payload_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["channel"] == "telegram"

    monkeypatch.setattr(
        channel_registry.get_adapter("telegram"),
        "send",
        lambda payload_json: SendResult(
            status="SENT",
            provider="telegram_bot_api",
            provider_message_id="123",
            request_json={"text": payload_json["text"]},
            response_json={"ok": True, "result": {"message_id": 123}},
        ),
    )
    send_response = client.post(f"/api/v1/payloads/{telegram_payload_id}/send")
    assert send_response.status_code == 200
    delivery_id = send_response.json()["data"]["delivery_id"]
    assert send_response.json()["data"]["status"] == "SENT"

    delivery_list_response = client.get(f"/api/v1/campaigns/{campaign_id}/delivery-logs")
    assert delivery_list_response.status_code == 200
    assert len(delivery_list_response.json()["data"]["delivery_logs"]) >= 1

    delivery_detail_response = client.get(f"/api/v1/delivery-logs/{delivery_id}")
    assert delivery_detail_response.status_code == 200
    assert delivery_detail_response.json()["data"]["provider_message_id"] == "123"

    whatsapp_send_response = client.post(f"/api/v1/payloads/{whatsapp_payload_id}/send")
    assert whatsapp_send_response.status_code == 400
    assert whatsapp_send_response.json()["error"]["code"] == "CHANNEL_SEND_NOT_SUPPORTED"


def test_slice_4_payload_generation_before_approval_and_unsupported_channel(client, monkeypatch):
    campaign_id, variants = _create_campaign_and_variants(client, monkeypatch)
    before_approval_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/payloads",
        json={"channels": ["telegram"], "regenerate": False},
    )
    assert before_approval_response.status_code == 400
    assert before_approval_response.json()["error"]["code"] == "CAMPAIGN_NOT_APPROVED"

    _approve_variant(client, variants[0]["variant_id"])
    unsupported_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/payloads",
        json={"channels": ["email"], "regenerate": False},
    )
    assert unsupported_response.status_code == 400
    assert unsupported_response.json()["error"]["code"] == "UNSUPPORTED_CHANNEL"


def test_slice_4_regenerate_and_missing_telegram_credentials(client, monkeypatch):
    campaign_id, variants = _create_campaign_and_variants(client, monkeypatch)
    _approve_variant(client, variants[0]["variant_id"])
    first_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/payloads",
        json={"channels": ["telegram"], "regenerate": False},
    )
    assert first_response.status_code == 200
    first_id = first_response.json()["data"]["payloads"][0]["payload_id"]
    second_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/payloads",
        json={"channels": ["telegram"], "regenerate": False},
    )
    assert second_response.status_code == 200
    assert second_response.json()["data"]["payloads"][0]["payload_id"] == first_id
    regenerated_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/payloads",
        json={"channels": ["telegram"], "regenerate": True},
    )
    assert regenerated_response.status_code == 200
    regenerated_id = regenerated_response.json()["data"]["payloads"][0]["payload_id"]
    assert regenerated_id != first_id

    monkeypatch.setattr(settings, "telegram_bot_token", "replace_me")
    monkeypatch.setattr(settings, "telegram_chat_id", "replace_me")
    send_response = client.post(f"/api/v1/payloads/{regenerated_id}/send")
    assert send_response.status_code == 400
    assert send_response.json()["error"]["code"] == "TELEGRAM_CREDENTIALS_MISSING"
