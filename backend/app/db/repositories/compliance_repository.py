from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ComplianceResult


def create_compliance_result(db: Session, values: dict[str, Any]) -> ComplianceResult:
    result = ComplianceResult(**values)
    db.add(result)
    db.flush()
    db.refresh(result)
    return result


def list_compliance_results(db: Session, variant_id: str) -> list[ComplianceResult]:
    return list(
        db.scalars(
            select(ComplianceResult)
            .where(ComplianceResult.variant_id == variant_id)
            .order_by(ComplianceResult.created_at.desc(), ComplianceResult.id.desc())
        ).all()
    )


def latest_compliance_result(db: Session, variant_id: str) -> ComplianceResult | None:
    return db.scalar(
        select(ComplianceResult)
        .where(ComplianceResult.variant_id == variant_id)
        .order_by(ComplianceResult.created_at.desc(), ComplianceResult.id.desc())
        .limit(1)
    )


def latest_results_for_campaign(db: Session, campaign_id: str) -> dict[str, ComplianceResult]:
    rows = list(
        db.scalars(
            select(ComplianceResult)
            .where(ComplianceResult.campaign_id == campaign_id)
            .order_by(ComplianceResult.variant_id.asc(), ComplianceResult.created_at.desc(), ComplianceResult.id.desc())
        ).all()
    )
    latest: dict[str, ComplianceResult] = {}
    for row in rows:
        latest.setdefault(row.variant_id, row)
    return latest
