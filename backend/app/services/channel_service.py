from __future__ import annotations

from sqlalchemy.orm import Session

from app.channels.channel_registry import channel_registry
from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, payload_repository, variant_repository
from app.schemas.payload_schema import (
    ChannelCapabilityData,
    ChannelListData,
    GeneratePayloadsData,
    GeneratePayloadsRequest,
    PayloadData,
    PayloadListData,
    PayloadReadinessData,
)

DEFAULT_CHANNELS = ["telegram", "whatsapp_mock"]


def list_channels() -> ChannelListData:
    return ChannelListData(channels=[ChannelCapabilityData(**item) for item in channel_registry.list_capabilities()])


def get_payload_readiness(db: Session, campaign_id: str) -> PayloadReadinessData:
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    missing: list[str] = []
    selected_variant = None
    if campaign.status != "APPROVED":
        missing.append("campaign must be APPROVED")
    if not campaign.selected_variant_id:
        missing.append("selected variant is required")
    else:
        selected_variant = variant_repository.get_variant(db, campaign.selected_variant_id)
        if selected_variant is None or selected_variant.campaign_id != campaign.id:
            missing.append("selected variant must exist for this campaign")
        elif selected_variant.status != "APPROVED":
            missing.append("selected variant must be APPROVED")
    return PayloadReadinessData(
        campaign_id=campaign.id,
        ready=not missing,
        campaign_status=campaign.status,
        selected_variant_id=campaign.selected_variant_id,
        selected_variant_status=selected_variant.status if selected_variant else None,
        missing_requirements=missing,
    )


def generate_payloads(db: Session, campaign_id: str, request: GeneratePayloadsRequest) -> GeneratePayloadsData:
    campaign, variant = _require_ready_campaign(db, campaign_id)
    channels = _normalize_channels(request.channels)
    if not request.regenerate:
        existing = payload_repository.latest_payloads_by_channel(db, campaign.id, channels)
        if all(channel in existing for channel in channels):
            return GeneratePayloadsData(
                campaign_id=campaign.id,
                selected_variant_id=variant.id,
                payloads=[_payload_data(existing[channel]) for channel in channels],
            )
    brief = campaign_repository.get_brief_for_campaign(db, campaign.id)
    rows = []
    for channel in channels:
        adapter = _adapter_for_channel(channel)
        built = adapter.build_payload(campaign=campaign, brief=brief, variant=variant)
        rows.append(
            payload_repository.create_payload(
                db,
                {
                    "id": new_id("payload"),
                    "campaign_id": campaign.id,
                    "variant_id": variant.id,
                    "channel": built.channel,
                    "payload_type": built.payload_type,
                    "payload_json": built.payload_json,
                    "preview_text": built.preview_text,
                    "status": "GENERATED",
                    "generated_by": "manager_default",
                },
            )
        )
    db.commit()
    for row in rows:
        db.refresh(row)
    return GeneratePayloadsData(campaign_id=campaign.id, selected_variant_id=variant.id, payloads=[_payload_data(row) for row in rows])


def list_payloads(db: Session, campaign_id: str, *, channel: str | None = None, status: str | None = None) -> PayloadListData:
    if campaign_repository.get_campaign(db, campaign_id) is None:
        raise ResourceNotFoundError("Campaign not found")
    if channel:
        _adapter_for_channel(channel)
    rows = payload_repository.list_payloads(db, campaign_id, channel=channel, status=status)
    return PayloadListData(campaign_id=campaign_id, payloads=[_payload_data(row) for row in rows])


def get_payload_detail(db: Session, payload_id: str) -> PayloadData:
    payload = payload_repository.get_payload(db, payload_id)
    if payload is None:
        raise ResourceNotFoundError("Payload not found")
    return _payload_data(payload)


def _require_ready_campaign(db: Session, campaign_id: str):
    campaign = campaign_repository.get_campaign(db, campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    if campaign.status != "APPROVED":
        raise ValidationError("Campaign must be approved before payload generation", code="CAMPAIGN_NOT_APPROVED")
    if not campaign.selected_variant_id:
        raise ValidationError("Selected variant is required before payload generation", code="SELECTED_VARIANT_REQUIRED")
    variant = variant_repository.get_variant(db, campaign.selected_variant_id)
    if variant is None or variant.campaign_id != campaign.id:
        raise ValidationError("Selected variant is required before payload generation", code="SELECTED_VARIANT_REQUIRED")
    if variant.status != "APPROVED":
        raise ValidationError("Selected variant must be approved before payload generation", code="SELECTED_VARIANT_NOT_APPROVED")
    return campaign, variant


def _normalize_channels(channels: list[str] | None) -> list[str]:
    requested = channels or DEFAULT_CHANNELS
    normalized: list[str] = []
    for channel in requested:
        if channel not in normalized:
            _adapter_for_channel(channel)
            normalized.append(channel)
    return normalized or DEFAULT_CHANNELS


def _adapter_for_channel(channel: str):
    try:
        return channel_registry.get_adapter(channel)
    except ValueError as exc:
        raise ValidationError("Unsupported channel", code="UNSUPPORTED_CHANNEL", details=[{"channel": channel}]) from exc


def _payload_data(row) -> PayloadData:
    return PayloadData(
        payload_id=row.id,
        campaign_id=row.campaign_id,
        variant_id=row.variant_id,
        channel=row.channel,
        payload_type=row.payload_type,
        payload_json=row.payload_json,
        preview_text=row.preview_text,
        status=row.status,
        error_message=row.error_message,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
