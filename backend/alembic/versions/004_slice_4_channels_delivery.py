"""create slice 4 channel payload and delivery tables

Revision ID: 004_slice_4
Revises: 003_slice_3
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_slice_4"
down_revision: str | None = "003_slice_3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "channel_payloads",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("variant_id", sa.String(length=50), sa.ForeignKey("message_variants.id"), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("payload_type", sa.String(length=100), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("preview_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("generated_by", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_channel_payloads_campaign_id", "channel_payloads", ["campaign_id"])
    op.create_index("ix_channel_payloads_variant_id", "channel_payloads", ["variant_id"])
    op.create_index("ix_channel_payloads_channel", "channel_payloads", ["channel"])
    op.create_index("ix_channel_payloads_status", "channel_payloads", ["status"])
    op.create_index("ix_channel_payloads_created_at", "channel_payloads", ["created_at"])

    op.create_table(
        "delivery_logs",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("variant_id", sa.String(length=50), sa.ForeignKey("message_variants.id"), nullable=False),
        sa.Column("payload_id", sa.String(length=50), sa.ForeignKey("channel_payloads.id"), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("provider_message_id", sa.String(length=150), nullable=True),
        sa.Column("request_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_delivery_logs_campaign_id", "delivery_logs", ["campaign_id"])
    op.create_index("ix_delivery_logs_variant_id", "delivery_logs", ["variant_id"])
    op.create_index("ix_delivery_logs_payload_id", "delivery_logs", ["payload_id"])
    op.create_index("ix_delivery_logs_channel", "delivery_logs", ["channel"])
    op.create_index("ix_delivery_logs_status", "delivery_logs", ["status"])
    op.create_index("ix_delivery_logs_created_at", "delivery_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_delivery_logs_created_at", table_name="delivery_logs")
    op.drop_index("ix_delivery_logs_status", table_name="delivery_logs")
    op.drop_index("ix_delivery_logs_channel", table_name="delivery_logs")
    op.drop_index("ix_delivery_logs_payload_id", table_name="delivery_logs")
    op.drop_index("ix_delivery_logs_variant_id", table_name="delivery_logs")
    op.drop_index("ix_delivery_logs_campaign_id", table_name="delivery_logs")
    op.drop_table("delivery_logs")
    op.drop_index("ix_channel_payloads_created_at", table_name="channel_payloads")
    op.drop_index("ix_channel_payloads_status", table_name="channel_payloads")
    op.drop_index("ix_channel_payloads_channel", table_name="channel_payloads")
    op.drop_index("ix_channel_payloads_variant_id", table_name="channel_payloads")
    op.drop_index("ix_channel_payloads_campaign_id", table_name="channel_payloads")
    op.drop_table("channel_payloads")
