from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Campaign, CampaignBrief, CampaignManager

DEFAULT_MANAGER_ID = "manager_default"


def ensure_default_manager(db: Session) -> CampaignManager:
    manager = db.get(CampaignManager, DEFAULT_MANAGER_ID)
    if manager is None:
        manager = CampaignManager(
            id=DEFAULT_MANAGER_ID,
            name="Local Campaign Manager",
            email="manager@example.com",
            role="campaign_manager",
        )
        db.add(manager)
        db.flush()
    return manager


def create_campaign(
    db: Session,
    *,
    campaign_id: str,
    campaign_name: str,
    goal: str | None = None,
    status: str = "DRAFT",
    created_by: str = DEFAULT_MANAGER_ID,
) -> Campaign:
    ensure_default_manager(db)
    campaign = Campaign(
        id=campaign_id,
        campaign_name=campaign_name,
        goal=goal,
        status=status,
        created_by=created_by,
        campaign_metadata={},
    )
    db.add(campaign)
    db.flush()
    db.refresh(campaign)
    return campaign


def get_campaign(db: Session, campaign_id: str) -> Campaign | None:
    return db.get(Campaign, campaign_id)


def list_campaigns(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
) -> tuple[list[Campaign], int]:
    stmt = select(Campaign)
    count_stmt = select(func.count()).select_from(Campaign)
    if status:
        stmt = stmt.where(Campaign.status == status)
        count_stmt = count_stmt.where(Campaign.status == status)
    total = db.scalar(count_stmt) or 0
    campaigns = list(
        db.scalars(stmt.order_by(Campaign.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    )
    return campaigns, total


def update_campaign_fields(db: Session, campaign: Campaign, fields: dict[str, object]) -> list[str]:
    updated: list[str] = []
    for field in ("campaign_name", "goal"):
        if field in fields:
            setattr(campaign, field, fields[field])
            updated.append(field)
    db.flush()
    db.refresh(campaign)
    return updated


def update_campaign_status(db: Session, campaign: Campaign, status: str) -> Campaign:
    campaign.status = status
    db.flush()
    db.refresh(campaign)
    return campaign


def select_variant(db: Session, campaign: Campaign, variant_id: str) -> Campaign:
    campaign.selected_variant_id = variant_id
    db.flush()
    db.refresh(campaign)
    return campaign


def count_total_pages(total_items: int, page_size: int) -> int:
    if total_items == 0:
        return 0
    return (total_items + page_size - 1) // page_size


def get_brief_for_campaign(db: Session, campaign_id: str) -> CampaignBrief | None:
    return db.scalar(select(CampaignBrief).where(CampaignBrief.campaign_id == campaign_id))


def normalize_updated_fields(*field_groups: Iterable[str]) -> list[str]:
    fields: list[str] = []
    for group in field_groups:
        for field in group:
            if field not in fields:
                fields.append(field)
    return fields
