from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EvaluationResult


def create_evaluation_result(db: Session, values: dict[str, Any]) -> EvaluationResult:
    result = EvaluationResult(**values)
    db.add(result)
    db.flush()
    db.refresh(result)
    return result


def get_evaluation_result(db: Session, evaluation_id: str) -> EvaluationResult | None:
    return db.get(EvaluationResult, evaluation_id)


def list_evaluation_results(
    db: Session,
    campaign_id: str,
    *,
    evaluation_type: str | None = None,
    variant_id: str | None = None,
) -> list[EvaluationResult]:
    stmt = select(EvaluationResult).where(EvaluationResult.campaign_id == campaign_id)
    if evaluation_type:
        stmt = stmt.where(EvaluationResult.evaluation_type == evaluation_type)
    if variant_id:
        stmt = stmt.where(EvaluationResult.variant_id == variant_id)
    return list(db.scalars(stmt.order_by(EvaluationResult.created_at.desc(), EvaluationResult.id.desc())).all())
