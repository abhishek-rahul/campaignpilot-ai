from app.channels.base_channel import BaseChannelAdapter


class ChannelRegistry:
    """Registry that prevents core services from calling provider adapters directly."""

    def __init__(self) -> None:
        self._adapters: dict[str, BaseChannelAdapter] = {}

    def register(self, adapter: BaseChannelAdapter) -> None:
        self._adapters[adapter.channel_name] = adapter

    def get(self, channel_name: str) -> BaseChannelAdapter:
        try:
            return self._adapters[channel_name]
        except KeyError as exc:
            raise ValueError(f"Unsupported channel: {channel_name}") from exc


channel_registry = ChannelRegistry()
