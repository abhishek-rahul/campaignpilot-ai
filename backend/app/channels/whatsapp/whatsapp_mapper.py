from __future__ import annotations

from typing import Any

from app.channels.base_channel import BuiltChannelPayload


def build_whatsapp_mock_payload(*, campaign: Any, brief: Any, variant: Any) -> BuiltChannelPayload:
    cta_link = getattr(brief, "cta_link", None) if brief else None
    payload_json = {
        "channel": "whatsapp_mock",
        "recipient_placeholder": "{{recipient_phone}}",
        "message_type": "text",
        "text": variant.message_body,
        "cta_link": cta_link,
        "template_variables": {
            "campaign_name": campaign.campaign_name,
            "offer_details": getattr(brief, "offer_details", None) if brief else None,
            "cta_link": cta_link,
        },
        "metadata": {
            "campaign_id": campaign.id,
            "variant_id": variant.id,
        },
    }
    return BuiltChannelPayload(
        channel="whatsapp_mock",
        payload_type="whatsapp_mock_template",
        payload_json=payload_json,
        preview_text=variant.message_body,
    )
