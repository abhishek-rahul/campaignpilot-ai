from types import SimpleNamespace

from app.channels.channel_registry import channel_registry
from app.channels.telegram.telegram_sender import TelegramAdapter
from app.channels.whatsapp.mock_whatsapp_sender import WhatsAppMockAdapter


def _objects():
    campaign = SimpleNamespace(id="camp_test", campaign_name="Festive Campaign")
    brief = SimpleNamespace(cta_link="https://example.com/sale", offer_details="25% discount")
    variant = SimpleNamespace(id="var_test", message_body="Friendly offer for you")
    return campaign, brief, variant


def test_telegram_payload_appends_cta_when_missing():
    campaign, brief, variant = _objects()
    payload = TelegramAdapter().build_payload(campaign=campaign, brief=brief, variant=variant)
    assert payload.channel == "telegram"
    assert payload.payload_type == "telegram_message"
    assert "https://example.com/sale" in payload.payload_json["text"]
    assert payload.payload_json["metadata"]["campaign_id"] == "camp_test"


def test_whatsapp_mock_payload_is_provider_neutral():
    campaign, brief, variant = _objects()
    payload = WhatsAppMockAdapter().build_payload(campaign=campaign, brief=brief, variant=variant)
    assert payload.channel == "whatsapp_mock"
    assert payload.payload_type == "whatsapp_mock_template"
    assert payload.payload_json["recipient_placeholder"] == "{{recipient_phone}}"
    assert payload.payload_json["message_type"] == "text"


def test_channel_registry_lists_supported_channels():
    assert channel_registry.list_supported_channels() == ["telegram", "whatsapp_mock"]
    assert channel_registry.list_send_supported_channels() == ["telegram"]
