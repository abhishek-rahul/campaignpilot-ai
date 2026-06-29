from __future__ import annotations

from app.channels.base_channel import BaseChannelAdapter, BuiltChannelPayload
from app.channels.whatsapp.whatsapp_mapper import build_whatsapp_mock_payload


class WhatsAppMockAdapter(BaseChannelAdapter):
    channel_name = "whatsapp_mock"
    payload_type = "whatsapp_mock_template"
    display_name = "WhatsApp Mock"
    supports_send = False

    def build_payload(self, *, campaign, brief, variant) -> BuiltChannelPayload:
        return build_whatsapp_mock_payload(campaign=campaign, brief=brief, variant=variant)
