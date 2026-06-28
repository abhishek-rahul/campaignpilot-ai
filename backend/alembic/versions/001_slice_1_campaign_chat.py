"""create slice 1 campaign chat tables

Revision ID: 001_slice_1
Revises:
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_slice_1"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "campaign_managers",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="campaign_manager"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "campaigns",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_name", sa.String(length=200), nullable=False),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("created_by", sa.String(length=50), sa.ForeignKey("campaign_managers.id"), nullable=True),
        sa.Column("selected_variant_id", sa.String(length=50), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_campaigns_created_by", "campaigns", ["created_by"])
    op.create_index("ix_campaigns_status", "campaigns", ["status"])
    op.create_index("ix_campaigns_created_at", "campaigns", ["created_at"])

    op.create_table(
        "campaign_briefs",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False, unique=True),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("target_audience", sa.String(length=150), nullable=True),
        sa.Column("offer_details", sa.Text(), nullable=True),
        sa.Column("tone", sa.String(length=100), nullable=True),
        sa.Column("preferred_channels", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("cta_link", sa.Text(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("missing_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("brief_status", sa.String(length=50), nullable=False, server_default="INCOMPLETE"),
        sa.Column("raw_user_input", sa.Text(), nullable=True),
        sa.Column("structured_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_campaign_briefs_campaign_id", "campaign_briefs", ["campaign_id"])

    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("sender", sa.String(length=50), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("message_type", sa.String(length=50), nullable=False, server_default="text"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_conversation_messages_campaign_id", "conversation_messages", ["campaign_id"])
    op.create_index("ix_conversation_messages_created_at", "conversation_messages", ["created_at"])

    op.create_table(
        "message_variants",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("variant_name", sa.String(length=150), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("message_body", sa.Text(), nullable=False),
        sa.Column("tone", sa.String(length=100), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="GENERATED"),
        sa.Column("context_refs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_message_variants_campaign_id", "message_variants", ["campaign_id"])
    op.create_index("ix_message_variants_channel", "message_variants", ["channel"])
    op.create_index("ix_message_variants_status", "message_variants", ["status"])

    op.create_table(
        "llm_traces",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("operation_name", sa.String(length=100), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("cost_estimate", sa.Numeric(12, 6), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="SUCCESS"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_llm_traces_campaign_id", "llm_traces", ["campaign_id"])
    op.create_index("ix_llm_traces_operation_name", "llm_traces", ["operation_name"])
    op.create_index("ix_llm_traces_created_at", "llm_traces", ["created_at"])

    op.bulk_insert(
        sa.table(
            "campaign_managers",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("email", sa.String),
            sa.column("role", sa.String),
        ),
        [{"id": "manager_default", "name": "Local Campaign Manager", "email": "manager@example.com", "role": "campaign_manager"}],
    )


def downgrade() -> None:
    op.drop_index("ix_llm_traces_created_at", table_name="llm_traces")
    op.drop_index("ix_llm_traces_operation_name", table_name="llm_traces")
    op.drop_index("ix_llm_traces_campaign_id", table_name="llm_traces")
    op.drop_table("llm_traces")
    op.drop_index("ix_message_variants_status", table_name="message_variants")
    op.drop_index("ix_message_variants_channel", table_name="message_variants")
    op.drop_index("ix_message_variants_campaign_id", table_name="message_variants")
    op.drop_table("message_variants")
    op.drop_index("ix_conversation_messages_created_at", table_name="conversation_messages")
    op.drop_index("ix_conversation_messages_campaign_id", table_name="conversation_messages")
    op.drop_table("conversation_messages")
    op.drop_index("ix_campaign_briefs_campaign_id", table_name="campaign_briefs")
    op.drop_table("campaign_briefs")
    op.drop_index("ix_campaigns_created_at", table_name="campaigns")
    op.drop_index("ix_campaigns_status", table_name="campaigns")
    op.drop_index("ix_campaigns_created_by", table_name="campaigns")
    op.drop_table("campaigns")
    op.drop_table("campaign_managers")
