from types import SimpleNamespace
from datetime import datetime, timezone

import pytest

from app.channels.base_channel import SendResult
from app.core.exceptions import CampaignPilotError, ValidationError
from app.services import delivery_service


def _approved_objects(channel="telegram"):
    payload = SimpleNamespace(
        id="payload_test",
        campaign_id="camp_test",
        variant_id="var_test",
        channel=channel,
        status="GENERATED",
        payload_json={"text": "hello"},
    )
    campaign = SimpleNamespace(id="camp_test", status="APPROVED", selected_variant_id="var_test")
    variant = SimpleNamespace(id="var_test", status="APPROVED")
    return payload, campaign, variant


def test_delivery_service_blocks_whatsapp_send(monkeypatch):
    payload, _, _ = _approved_objects(channel="whatsapp_mock")
    monkeypatch.setattr(delivery_service.payload_repository, "get_payload", lambda db, payload_id: payload)
    with pytest.raises(ValidationError) as exc:
        delivery_service.send_payload(None, "payload_test")
    assert exc.value.code == "CHANNEL_SEND_NOT_SUPPORTED"


def test_delivery_service_persists_success(monkeypatch):
    payload, campaign, variant = _approved_objects()
    saved = SimpleNamespace(
        id="del_test",
        payload_id=payload.id,
        campaign_id=campaign.id,
        variant_id=variant.id,
        channel="telegram",
        status="SENT",
        provider="telegram_bot_api",
        provider_message_id="123",
        request_json={},
        response_json={},
        error_message=None,
        sent_at=None,
        created_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(delivery_service.payload_repository, "get_payload", lambda db, payload_id: payload)
    monkeypatch.setattr(delivery_service.campaign_repository, "get_campaign", lambda db, campaign_id: campaign)
    monkeypatch.setattr(delivery_service.variant_repository, "get_variant", lambda db, variant_id: variant)
    monkeypatch.setattr(
        delivery_service.channel_registry.get_adapter("telegram"),
        "send",
        lambda payload_json: SendResult(status="SENT", provider="telegram_bot_api", provider_message_id="123"),
    )
    monkeypatch.setattr(delivery_service.delivery_repository, "create_delivery_log", lambda db, values: saved)
    db = SimpleNamespace(commit=lambda: None, refresh=lambda row: None)
    result = delivery_service.send_payload(db, "payload_test")
    assert result.status == "SENT"


def test_delivery_service_persists_failure_and_raises(monkeypatch):
    payload, campaign, variant = _approved_objects()
    saved = SimpleNamespace(
        id="del_test",
        payload_id=payload.id,
        campaign_id=campaign.id,
        variant_id=variant.id,
        channel="telegram",
        status="FAILED",
        provider="telegram_bot_api",
        provider_message_id=None,
        request_json={},
        response_json={},
        error_message="boom",
        sent_at=None,
        created_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(delivery_service.payload_repository, "get_payload", lambda db, payload_id: payload)
    monkeypatch.setattr(delivery_service.campaign_repository, "get_campaign", lambda db, campaign_id: campaign)
    monkeypatch.setattr(delivery_service.variant_repository, "get_variant", lambda db, variant_id: variant)
    monkeypatch.setattr(
        delivery_service.channel_registry.get_adapter("telegram"),
        "send",
        lambda payload_json: SendResult(status="FAILED", provider="telegram_bot_api", error_message="boom"),
    )
    monkeypatch.setattr(delivery_service.delivery_repository, "create_delivery_log", lambda db, values: saved)
    db = SimpleNamespace(commit=lambda: None, refresh=lambda row: None)
    with pytest.raises(CampaignPilotError) as exc:
        delivery_service.send_payload(db, "payload_test")
    assert exc.value.code == "TELEGRAM_SEND_FAILED"
