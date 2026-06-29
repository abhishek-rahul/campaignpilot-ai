from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BuiltChannelPayload:
    channel: str
    payload_type: str
    payload_json: dict[str, Any]
    preview_text: str


@dataclass(frozen=True)
class SendResult:
    status: str
    provider: str
    provider_message_id: str | None = None
    request_json: dict[str, Any] | None = None
    response_json: dict[str, Any] | None = None
    error_message: str | None = None


class BaseChannelAdapter(ABC):
    """Common interface for all messaging channels."""

    channel_name: str
    payload_type: str
    display_name: str
    supports_send: bool = False

    @abstractmethod
    def build_payload(self, *, campaign: Any, brief: Any, variant: Any) -> BuiltChannelPayload:
        """Build a provider-specific payload for the approved variant."""

    def send(self, payload_json: dict[str, Any]) -> SendResult:
        """Send payload when supported by the adapter."""
        raise NotImplementedError("Channel does not support sending")
