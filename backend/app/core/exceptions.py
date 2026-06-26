class CampaignPilotError(Exception):
    """Base exception for CampaignPilot AI."""


class InvalidStateError(CampaignPilotError):
    """Raised when a business workflow state is invalid."""
