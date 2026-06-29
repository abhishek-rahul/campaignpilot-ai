from __future__ import annotations

from app.channels.base_channel import BaseChannelAdapter
from app.channels.telegram.telegram_sender import TelegramAdapter
from app.channels.whatsapp.mock_whatsapp_sender import WhatsAppMockAdapter


class ChannelRegistry:
    """Registry that prevents services from depending on concrete providers."""

    def __init__(self) -> None:
        self._adapters: dict[str, BaseChannelAdapter] = {}

    def register(self, adapter: BaseChannelAdapter) -> None:
        self._adapters[adapter.channel_name] = adapter

    def get_adapter(self, channel_name: str) -> BaseChannelAdapter:
        try:
            return self._adapters[channel_name]
        except KeyError as exc:
            raise ValueError(f"Unsupported channel: {channel_name}") from exc

    def get(self, channel_name: str) -> BaseChannelAdapter:
        return self.get_adapter(channel_name)

    def list_supported_channels(self) -> list[str]:
        return sorted(self._adapters)

    def list_send_supported_channels(self) -> list[str]:
        return sorted(name for name, adapter in self._adapters.items() if adapter.supports_send)

    def list_capabilities(self) -> list[dict[str, object]]:
        return [
            {
                "channel": adapter.channel_name,
                "display_name": adapter.display_name,
                "is_active": True,
                "supports_payload_generation": True,
                "supports_send": adapter.supports_send,
                "payload_type": adapter.payload_type,
            }
            for adapter in self._adapters.values()
        ]


channel_registry = ChannelRegistry()
channel_registry.register(TelegramAdapter())
channel_registry.register(WhatsAppMockAdapter())
