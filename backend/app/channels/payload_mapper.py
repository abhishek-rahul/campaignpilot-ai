from typing import Any


def build_generic_payload(**kwargs: Any) -> dict[str, Any]:
    """Build provider-independent campaign payload."""
    return dict(kwargs)
