from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CampaignRefinement


def create_refinement(db: Session, values: dict[str, Any]) -> CampaignRefinement:
    refinement = CampaignRefinement(**values)
    db.add(refinement)
    db.flush()
    db.refresh(refinement)
    return refinement


def list_refinements(
    db: Session,
    campaign_id: str,
    *,
    refinement_type: str | None = None,
    source_type: str | None = None,
) -> list[CampaignRefinement]:
    stmt = select(CampaignRefinement).where(CampaignRefinement.campaign_id == campaign_id)
    if refinement_type:
        stmt = stmt.where(CampaignRefinement.refinement_type == refinement_type)
    if source_type:
        stmt = stmt.where(CampaignRefinement.source_type == source_type)
    return list(db.scalars(stmt.order_by(CampaignRefinement.created_at.desc(), CampaignRefinement.id.desc())).all())
