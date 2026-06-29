"""create slice 3 compliance approval tables

Revision ID: 003_slice_3
Revises: 002_slice_2
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_slice_3"
down_revision: str | None = "002_slice_2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "compliance_results",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("variant_id", sa.String(length=50), sa.ForeignKey("message_variants.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("issues_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("checked_rules_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("source_context_ids_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("raw_result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_compliance_results_campaign_id", "compliance_results", ["campaign_id"])
    op.create_index("ix_compliance_results_variant_id", "compliance_results", ["variant_id"])
    op.create_index("ix_compliance_results_status", "compliance_results", ["status"])
    op.create_index("ix_compliance_results_created_at", "compliance_results", ["created_at"])

    op.create_table(
        "approvals",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("variant_id", sa.String(length=50), sa.ForeignKey("message_variants.id"), nullable=False),
        sa.Column("approval_status", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("actor_id", sa.String(length=50), nullable=True),
        sa.Column("previous_status", sa.String(length=50), nullable=False),
        sa.Column("new_status", sa.String(length=50), nullable=False),
        sa.Column("override_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_approvals_campaign_id", "approvals", ["campaign_id"])
    op.create_index("ix_approvals_variant_id", "approvals", ["variant_id"])
    op.create_index("ix_approvals_approval_status", "approvals", ["approval_status"])

    op.create_table(
        "tool_call_logs",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("variant_id", sa.String(length=50), sa.ForeignKey("message_variants.id"), nullable=True),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("input_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("output_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tool_call_logs_campaign_id", "tool_call_logs", ["campaign_id"])
    op.create_index("ix_tool_call_logs_variant_id", "tool_call_logs", ["variant_id"])
    op.create_index("ix_tool_call_logs_tool_name", "tool_call_logs", ["tool_name"])
    op.create_index("ix_tool_call_logs_created_at", "tool_call_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_tool_call_logs_created_at", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_tool_name", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_variant_id", table_name="tool_call_logs")
    op.drop_index("ix_tool_call_logs_campaign_id", table_name="tool_call_logs")
    op.drop_table("tool_call_logs")
    op.drop_index("ix_approvals_approval_status", table_name="approvals")
    op.drop_index("ix_approvals_variant_id", table_name="approvals")
    op.drop_index("ix_approvals_campaign_id", table_name="approvals")
    op.drop_table("approvals")
    op.drop_index("ix_compliance_results_created_at", table_name="compliance_results")
    op.drop_index("ix_compliance_results_status", table_name="compliance_results")
    op.drop_index("ix_compliance_results_variant_id", table_name="compliance_results")
    op.drop_index("ix_compliance_results_campaign_id", table_name="compliance_results")
    op.drop_table("compliance_results")
