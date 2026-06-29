from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DeliveryLog


def create_delivery_log(db: Session, values: dict[str, Any]) -> DeliveryLog:
    log = DeliveryLog(**values)
    db.add(log)
    db.flush()
    db.refresh(log)
    return log


def get_delivery_log(db: Session, delivery_id: str) -> DeliveryLog | None:
    return db.get(DeliveryLog, delivery_id)


def list_delivery_logs(
    db: Session,
    campaign_id: str,
    *,
    channel: str | None = None,
    status: str | None = None,
) -> list[DeliveryLog]:
    stmt = select(DeliveryLog).where(DeliveryLog.campaign_id == campaign_id)
    if channel:
        stmt = stmt.where(DeliveryLog.channel == channel)
    if status:
        stmt = stmt.where(DeliveryLog.status == status)
    return list(db.scalars(stmt.order_by(DeliveryLog.created_at.desc(), DeliveryLog.id.desc())).all())
