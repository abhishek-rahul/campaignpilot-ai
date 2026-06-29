from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ChannelPayload


def create_payload(db: Session, values: dict[str, Any]) -> ChannelPayload:
    payload = ChannelPayload(**values)
    db.add(payload)
    db.flush()
    db.refresh(payload)
    return payload


def get_payload(db: Session, payload_id: str) -> ChannelPayload | None:
    return db.get(ChannelPayload, payload_id)


def list_payloads(
    db: Session,
    campaign_id: str,
    *,
    channels: list[str] | None = None,
    channel: str | None = None,
    status: str | None = None,
) -> list[ChannelPayload]:
    stmt = select(ChannelPayload).where(ChannelPayload.campaign_id == campaign_id)
    if channels:
        stmt = stmt.where(ChannelPayload.channel.in_(channels))
    if channel:
        stmt = stmt.where(ChannelPayload.channel == channel)
    if status:
        stmt = stmt.where(ChannelPayload.status == status)
    return list(db.scalars(stmt.order_by(ChannelPayload.created_at.desc(), ChannelPayload.id.desc())).all())


def latest_payloads_by_channel(db: Session, campaign_id: str, channels: list[str]) -> dict[str, ChannelPayload]:
    rows = list_payloads(db, campaign_id, channels=channels, status="GENERATED")
    latest: dict[str, ChannelPayload] = {}
    for row in rows:
        latest.setdefault(row.channel, row)
    return latest
