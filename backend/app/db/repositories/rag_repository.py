from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RetrievedContext


def create_retrieved_contexts(db: Session, contexts: list[dict[str, Any]]) -> list[RetrievedContext]:
    models = [RetrievedContext(**context) for context in contexts]
    db.add_all(models)
    db.flush()
    for model in models:
        db.refresh(model)
    return models


def list_retrieved_contexts(
    db: Session,
    campaign_id: str,
    *,
    used_for: str | None = None,
    limit: int = 20,
) -> list[RetrievedContext]:
    stmt = (
        select(RetrievedContext)
        .where(RetrievedContext.campaign_id == campaign_id)
        .order_by(RetrievedContext.created_at.desc(), RetrievedContext.rank_position.asc())
        .limit(limit)
    )
    if used_for:
        stmt = stmt.where(RetrievedContext.used_for == used_for)
    return list(db.scalars(stmt).all())
