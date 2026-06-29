from types import SimpleNamespace

import pytest

from app.core.exceptions import ValidationError
from app.services import channel_service


def test_payload_service_blocks_unapproved_campaign(monkeypatch):
    campaign = SimpleNamespace(id="camp_test", status="DRAFT", selected_variant_id="var_test")
    monkeypatch.setattr(channel_service.campaign_repository, "get_campaign", lambda db, campaign_id: campaign)
    with pytest.raises(ValidationError) as exc:
        channel_service.generate_payloads(None, "camp_test", channel_service.GeneratePayloadsRequest())
    assert exc.value.code == "CAMPAIGN_NOT_APPROVED"


def test_payload_service_blocks_missing_selected_variant(monkeypatch):
    campaign = SimpleNamespace(id="camp_test", status="APPROVED", selected_variant_id=None)
    monkeypatch.setattr(channel_service.campaign_repository, "get_campaign", lambda db, campaign_id: campaign)
    with pytest.raises(ValidationError) as exc:
        channel_service.generate_payloads(None, "camp_test", channel_service.GeneratePayloadsRequest())
    assert exc.value.code == "SELECTED_VARIANT_REQUIRED"


def test_payload_service_blocks_unapproved_selected_variant(monkeypatch):
    campaign = SimpleNamespace(id="camp_test", status="APPROVED", selected_variant_id="var_test")
    variant = SimpleNamespace(id="var_test", campaign_id="camp_test", status="GENERATED")
    monkeypatch.setattr(channel_service.campaign_repository, "get_campaign", lambda db, campaign_id: campaign)
    monkeypatch.setattr(channel_service.variant_repository, "get_variant", lambda db, variant_id: variant)
    with pytest.raises(ValidationError) as exc:
        channel_service.generate_payloads(None, "camp_test", channel_service.GeneratePayloadsRequest())
    assert exc.value.code == "SELECTED_VARIANT_NOT_APPROVED"


def test_payload_service_unsupported_channel(monkeypatch):
    campaign = SimpleNamespace(id="camp_test", status="APPROVED", selected_variant_id="var_test")
    variant = SimpleNamespace(id="var_test", campaign_id="camp_test", status="APPROVED")
    monkeypatch.setattr(channel_service.campaign_repository, "get_campaign", lambda db, campaign_id: campaign)
    monkeypatch.setattr(channel_service.variant_repository, "get_variant", lambda db, variant_id: variant)
    with pytest.raises(ValidationError) as exc:
        channel_service.generate_payloads(
            None,
            "camp_test",
            channel_service.GeneratePayloadsRequest(channels=["email"]),
        )
    assert exc.value.code == "UNSUPPORTED_CHANNEL"
