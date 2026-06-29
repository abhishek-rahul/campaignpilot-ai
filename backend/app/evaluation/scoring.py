from __future__ import annotations

from app.schemas.evaluation_schema import EvaluationCheckData


def grade_for_score(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def passed_for_checks(score: int, checks: list[EvaluationCheckData]) -> bool:
    return score >= 70 and not any((not check.passed) and check.high_risk for check in checks)
