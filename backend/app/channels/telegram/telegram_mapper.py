from __future__ import annotations

from typing import Any

from app.channels.base_channel import BuiltChannelPayload


def build_telegram_payload(*, campaign: Any, brief: Any, variant: Any) -> BuiltChannelPayload:
    cta_link = getattr(brief, "cta_link", None) if brief else None
    text = variant.message_body
    if cta_link and cta_link not in text:
        text = f"{text}\n\n{cta_link}"
    payload_json = {
        "channel": "telegram",
        "text": text,
        "parse_mode": None,
        "disable_web_page_preview": False,
        "cta_link": cta_link,
        "metadata": {
            "campaign_id": campaign.id,
            "variant_id": variant.id,
        },
    }
    return BuiltChannelPayload(
        channel="telegram",
        payload_type="telegram_message",
        payload_json=payload_json,
        preview_text=text,
    )
