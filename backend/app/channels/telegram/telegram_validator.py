from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import ValidationError


def has_telegram_credentials() -> bool:
    token = _usable_value(settings.telegram_bot_token)
    chat_id = _usable_value(settings.telegram_chat_id) or _usable_value(settings.telegram_default_chat_id)
    return bool(token and chat_id)


def require_telegram_credentials() -> tuple[str, str]:
    token = _usable_value(settings.telegram_bot_token)
    chat_id = _usable_value(settings.telegram_chat_id) or _usable_value(settings.telegram_default_chat_id)
    if not token or not chat_id:
        raise ValidationError("Telegram credentials are missing", code="TELEGRAM_CREDENTIALS_MISSING")
    return token, chat_id


def _usable_value(value: str | None) -> str | None:
    normalized = (value or "").strip()
    if not normalized or normalized == "replace_me":
        return None
    return normalized
