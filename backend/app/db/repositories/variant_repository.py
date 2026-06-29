from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MessageVariant


def create_variants(db: Session, variants: list[dict[str, Any]]) -> list[MessageVariant]:
    models = [MessageVariant(**variant) for variant in variants]
    db.add_all(models)
    db.flush()
    for model in models:
        db.refresh(model)
    return models


def list_variants(db: Session, campaign_id: str) -> list[MessageVariant]:
    return list(
        db.scalars(
            select(MessageVariant)
            .where(MessageVariant.campaign_id == campaign_id)
            .order_by(MessageVariant.created_at.asc(), MessageVariant.id.asc())
        ).all()
    )


def get_variant(db: Session, variant_id: str) -> MessageVariant | None:
    return db.get(MessageVariant, variant_id)


def update_variant_fields(db: Session, variant: MessageVariant, fields: dict[str, object]) -> list[str]:
    updated: list[str] = []
    for field in ("variant_name", "message_body", "tone", "reason", "risk_level"):
        if field in fields:
            setattr(variant, field, fields[field])
            updated.append(field)
    db.flush()
    db.refresh(variant)
    return updated


def update_variant_status(db: Session, variant: MessageVariant, status: str) -> MessageVariant:
    variant.status = status
    db.flush()
    db.refresh(variant)
    return variant


def update_variant_risk_and_status(
    db: Session,
    variant: MessageVariant,
    *,
    risk_level: str | None = None,
    status: str | None = None,
) -> MessageVariant:
    if risk_level is not None:
        variant.risk_level = risk_level
    if status is not None:
        variant.status = status
    db.flush()
    db.refresh(variant)
    return variant
