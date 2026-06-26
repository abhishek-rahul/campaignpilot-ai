from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseChannelAdapter(ABC):
    """Common interface for all messaging channels."""

    channel_name: str

    @abstractmethod
    def validate_payload(self, payload: dict[str, Any]) -> None:
        """Validate provider-specific payload before send/mock."""

    @abstractmethod
    def map_payload(self, generic_payload: dict[str, Any]) -> dict[str, Any]:
        """Convert generic campaign payload into provider-specific payload."""

    @abstractmethod
    async def send_text(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send or mock-send text payload."""
