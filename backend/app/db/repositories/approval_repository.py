from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Approval


def create_approval(db: Session, values: dict[str, Any]) -> Approval:
    approval = Approval(**values)
    db.add(approval)
    db.flush()
    db.refresh(approval)
    return approval


def latest_approval_for_variant(db: Session, variant_id: str) -> Approval | None:
    return db.scalar(
        select(Approval)
        .where(Approval.variant_id == variant_id)
        .order_by(Approval.created_at.desc(), Approval.id.desc())
        .limit(1)
    )
