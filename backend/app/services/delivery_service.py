from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.channels.channel_registry import channel_registry
from app.core.exceptions import CampaignPilotError, ResourceNotFoundError, ValidationError
from app.core.ids import new_id
from app.db.repositories import campaign_repository, delivery_repository, payload_repository, variant_repository
from app.schemas.delivery_schema import DeliveryLogData, DeliveryLogListData, SendPayloadData


def send_payload(db: Session, payload_id: str) -> SendPayloadData:
    payload = payload_repository.get_payload(db, payload_id)
    if payload is None:
        raise ResourceNotFoundError("Payload not found")
    if payload.channel != "telegram":
        raise ValidationError("Sending is not supported for this channel", code="CHANNEL_SEND_NOT_SUPPORTED")
    if payload.status != "GENERATED":
        raise ValidationError("Payload is not ready to send", code="PAYLOAD_NOT_READY")
    campaign = campaign_repository.get_campaign(db, payload.campaign_id)
    if campaign is None:
        raise ResourceNotFoundError("Campaign not found")
    if campaign.status != "APPROVED":
        raise ValidationError("Campaign must be approved before sending", code="CAMPAIGN_NOT_APPROVED")
    if campaign.selected_variant_id != payload.variant_id:
        raise ValidationError("Payload is not for the selected campaign variant", code="SELECTED_VARIANT_REQUIRED")
    variant = variant_repository.get_variant(db, payload.variant_id)
    if variant is None or variant.status != "APPROVED":
        raise ValidationError("Selected variant must be approved before sending", code="SELECTED_VARIANT_NOT_APPROVED")
    adapter = channel_registry.get_adapter(payload.channel)
    result = adapter.send(payload.payload_json)
    sent_at = datetime.now(timezone.utc) if result.status == "SENT" else None
    row = delivery_repository.create_delivery_log(
        db,
        {
            "id": new_id("del"),
            "campaign_id": payload.campaign_id,
            "variant_id": payload.variant_id,
            "payload_id": payload.id,
            "channel": payload.channel,
            "status": result.status,
            "provider": result.provider,
            "provider_message_id": result.provider_message_id,
            "request_json": result.request_json or {},
            "response_json": result.response_json or {},
            "error_message": result.error_message,
            "sent_at": sent_at,
        },
    )
    db.commit()
    db.refresh(row)
    if result.status == "FAILED":
        raise CampaignPilotError(
            "Telegram send failed",
            code="TELEGRAM_SEND_FAILED",
            status_code=502,
            details=[{"delivery_id": row.id, "error_message": row.error_message}],
        )
    return _send_data(row)


def list_delivery_logs(db: Session, campaign_id: str, *, channel: str | None = None, status: str | None = None) -> DeliveryLogListData:
    if campaign_repository.get_campaign(db, campaign_id) is None:
        raise ResourceNotFoundError("Campaign not found")
    rows = delivery_repository.list_delivery_logs(db, campaign_id, channel=channel, status=status)
    return DeliveryLogListData(campaign_id=campaign_id, delivery_logs=[_delivery_data(row) for row in rows])


def get_delivery_detail(db: Session, delivery_id: str) -> DeliveryLogData:
    row = delivery_repository.get_delivery_log(db, delivery_id)
    if row is None:
        raise ResourceNotFoundError("Delivery log not found")
    return _delivery_data(row)


def _send_data(row) -> SendPayloadData:
    return SendPayloadData(
        delivery_id=row.id,
        payload_id=row.payload_id,
        campaign_id=row.campaign_id,
        variant_id=row.variant_id,
        channel=row.channel,
        status=row.status,
        provider=row.provider,
        provider_message_id=row.provider_message_id,
        error_message=row.error_message,
        sent_at=row.sent_at,
        created_at=row.created_at,
    )


def _delivery_data(row) -> DeliveryLogData:
    return DeliveryLogData(
        delivery_id=row.id,
        payload_id=row.payload_id,
        campaign_id=row.campaign_id,
        variant_id=row.variant_id,
        channel=row.channel,
        status=row.status,
        provider=row.provider,
        provider_message_id=row.provider_message_id,
        request_json=row.request_json,
        response_json=row.response_json,
        error_message=row.error_message,
        sent_at=row.sent_at,
        created_at=row.created_at,
    )
