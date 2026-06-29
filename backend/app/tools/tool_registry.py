from app.tools.compliance_rules import ALL_RULES


def list_compliance_tools() -> list[str]:
    return [getattr(rule, "__name__", "unknown_rule") for rule in ALL_RULES]
