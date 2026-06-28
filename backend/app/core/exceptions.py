class CampaignPilotError(Exception):
    """Base exception for CampaignPilot AI."""

    def __init__(self, message: str, code: str = "CAMPAIGNPILOT_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class InvalidStateError(CampaignPilotError):
    """Raised when a business workflow state is invalid."""


class ResourceNotFoundError(CampaignPilotError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="RESOURCE_NOT_FOUND", status_code=404)


class ValidationError(CampaignPilotError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)


class LLMError(CampaignPilotError):
    def __init__(self, message: str = "LLM provider failed"):
        super().__init__(message, code="LLM_PROVIDER_ERROR", status_code=500)
