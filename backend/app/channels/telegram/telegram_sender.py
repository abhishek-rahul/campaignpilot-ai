from __future__ import annotations

import httpx

from app.channels.base_channel import BaseChannelAdapter, BuiltChannelPayload, SendResult
from app.channels.telegram.telegram_mapper import build_telegram_payload
from app.channels.telegram.telegram_validator import require_telegram_credentials


class TelegramAdapter(BaseChannelAdapter):
    channel_name = "telegram"
    payload_type = "telegram_message"
    display_name = "Telegram"
    supports_send = True

    def build_payload(self, *, campaign, brief, variant) -> BuiltChannelPayload:
        return build_telegram_payload(campaign=campaign, brief=brief, variant=variant)

    def send(self, payload_json: dict) -> SendResult:
        token, chat_id = require_telegram_credentials()
        request_json = {
            "chat_id": chat_id,
            "text": payload_json["text"],
            "parse_mode": payload_json.get("parse_mode"),
            "disable_web_page_preview": payload_json.get("disable_web_page_preview", False),
        }
        request_json = {key: value for key, value in request_json.items() if value is not None}
        try:
            response = httpx.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json=request_json,
                timeout=15,
            )
            response_json = response.json()
        except Exception as exc:
            return SendResult(
                status="FAILED",
                provider="telegram_bot_api",
                request_json=request_json,
                response_json={},
                error_message=str(exc),
            )
        if response.status_code >= 400 or not response_json.get("ok", False):
            return SendResult(
                status="FAILED",
                provider="telegram_bot_api",
                request_json=request_json,
                response_json=response_json,
                error_message=response_json.get("description") or f"Telegram HTTP {response.status_code}",
            )
        result = response_json.get("result") or {}
        return SendResult(
            status="SENT",
            provider="telegram_bot_api",
            provider_message_id=str(result.get("message_id")) if result.get("message_id") is not None else None,
            request_json=request_json,
            response_json=response_json,
            error_message=None,
        )
