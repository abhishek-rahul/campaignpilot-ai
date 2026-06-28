import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.main import app


pytestmark = pytest.mark.integration


def _database_available() -> bool:
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with engine.connect() as connection:
            connection.execute(text("select 1"))
            connection.execute(text("select 1 from brand_documents limit 1"))
        return True
    except SQLAlchemyError:
        return False


@pytest.fixture(scope="module")
def client():
    if not _database_available():
        pytest.skip("Configured database/migration is not available; run docker compose and alembic.")
    return TestClient(app)


def _create_campaign(client: TestClient) -> str:
    response = client.post(
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
    assert response.status_code == 200
    return response.json()["data"]["campaign_id"]


def test_slice_2_document_rag_flow(client):
    campaign_id = _create_campaign(client)
    content = b"Brand voice must be friendly. Mention VIP festive access and keep the CTA direct."
    upload_response = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "brand_guideline", "campaign_id": campaign_id},
        files={"file": ("brand.txt", io.BytesIO(content), "text/plain")},
    )
    assert upload_response.status_code == 200
    document_id = upload_response.json()["data"]["document_id"]

    detail_response = client.get(f"/api/v1/documents/{document_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["status"] == "UPLOADED"

    ingest_response = client.post(f"/api/v1/documents/{document_id}/ingest", json={})
    assert ingest_response.status_code == 200
    assert ingest_response.json()["data"]["chunks_count"] >= 1

    context_response = client.get(f"/api/v1/campaigns/{campaign_id}/retrieved-context?refresh=true")
    assert context_response.status_code == 200
    assert context_response.json()["data"]["campaign_id"] == campaign_id

    plan_response = client.post(f"/api/v1/campaigns/{campaign_id}/plan")
    assert plan_response.status_code == 200
    assert "plan" in plan_response.json()["data"]

    variants_response = client.post(
        f"/api/v1/campaigns/{campaign_id}/generate-variants",
        json={"variant_count": 3, "use_rag_context": True, "use_memory": False},
    )
    assert variants_response.status_code == 200
    assert len(variants_response.json()["data"]["variants"]) == 3


def test_slice_2_unsupported_upload(client):
    response = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "brand_guideline"},
        files={"file": ("brand.docx", io.BytesIO(b"not supported"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"
