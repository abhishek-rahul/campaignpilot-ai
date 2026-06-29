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
            connection.execute(text("select 1 from compliance_results limit 1"))
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


def test_slice_3_compliance_approval_flow(client, monkeypatch):
    campaign_id, variants = _create_campaign_and_variants(client, monkeypatch)
    variant_id = variants[0]["variant_id"]

    check_response = client.post(f"/api/v1/variants/{variant_id}/compliance-check", json={"use_rag_context": False})
    assert check_response.status_code == 200
    assert check_response.json()["data"]["status"] in {"PASSED", "WARNING"}

    list_response = client.get(f"/api/v1/variants/{variant_id}/compliance-checks")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]["checks"]) >= 1

    approve_response = client.post(f"/api/v1/variants/{variant_id}/approve", json={"reason": "Looks good"})
    assert approve_response.status_code == 200
    assert approve_response.json()["data"]["status"] == "APPROVED"

    reject_response = client.post(f"/api/v1/variants/{variants[1]['variant_id']}/reject", json={"reason": "Too aggressive"})
    assert reject_response.status_code == 200
    assert reject_response.json()["data"]["status"] == "REJECTED"

    summary_response = client.get(f"/api/v1/campaigns/{campaign_id}/compliance-summary")
    assert summary_response.status_code == 200
    assert summary_response.json()["data"]["approved_count"] >= 1
    assert summary_response.json()["data"]["rejected_count"] >= 1


def test_slice_3_blocks_failed_variant_without_override(client, monkeypatch):
    _, variants = _create_campaign_and_variants(client, monkeypatch)
    variant_id = variants[0]["variant_id"]
    patch_response = client.patch(
        f"/api/v1/variants/{variant_id}",
        json={"message_body": "Last chance! Guaranteed savings with 50% discount. Hurry now!!! 🔥🔥🔥🔥"},
    )
    assert patch_response.status_code == 200

    check_response = client.post(f"/api/v1/variants/{variant_id}/compliance-check", json={"use_rag_context": False})
    assert check_response.status_code == 200
    assert check_response.json()["data"]["status"] == "FAILED"

    blocked_response = client.post(f"/api/v1/variants/{variant_id}/approve", json={"reason": "No override"})
    assert blocked_response.status_code == 400
    assert blocked_response.json()["error"]["code"] == "VARIANT_NOT_COMPLIANT"

    override_response = client.post(
        f"/api/v1/variants/{variant_id}/approve",
        json={"reason": "Manual override for demo", "allow_high_risk_override": True},
    )
    assert override_response.status_code == 200
    assert override_response.json()["data"]["override_used"] is True
