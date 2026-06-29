import pytest

from app.channels.telegram.telegram_sender import TelegramAdapter
from app.channels.telegram.telegram_validator import require_telegram_credentials
from app.core.exceptions import ValidationError


def test_telegram_credentials_missing_for_replace_me(monkeypatch):
    from app.channels.telegram import telegram_validator

    monkeypatch.setattr(telegram_validator.settings, "telegram_bot_token", "replace_me")
    monkeypatch.setattr(telegram_validator.settings, "telegram_chat_id", "replace_me")
    with pytest.raises(ValidationError) as exc:
        require_telegram_credentials()
    assert exc.value.code == "TELEGRAM_CREDENTIALS_MISSING"


def test_telegram_send_method_is_mockable(monkeypatch):
    adapter = TelegramAdapter()
    monkeypatch.setattr(adapter, "send", lambda payload: {"ok": True})
    assert adapter.send({"text": "hello"}) == {"ok": True}
