"""create slice 5 streaming refinement tables

Revision ID: 005_slice_5
Revises: 004_slice_4
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_slice_5"
down_revision: str | None = "004_slice_4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "campaign_refinements",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=50), nullable=True),
        sa.Column("refinement_type", sa.String(length=50), nullable=False),
        sa.Column("user_feedback", sa.Text(), nullable=False),
        sa.Column("before_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("after_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("llm_trace_id", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_campaign_refinements_campaign_id", "campaign_refinements", ["campaign_id"])
    op.create_index("ix_campaign_refinements_source_type", "campaign_refinements", ["source_type"])
    op.create_index("ix_campaign_refinements_source_id", "campaign_refinements", ["source_id"])
    op.create_index("ix_campaign_refinements_refinement_type", "campaign_refinements", ["refinement_type"])
    op.create_index("ix_campaign_refinements_status", "campaign_refinements", ["status"])
    op.create_index("ix_campaign_refinements_created_at", "campaign_refinements", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_campaign_refinements_created_at", table_name="campaign_refinements")
    op.drop_index("ix_campaign_refinements_status", table_name="campaign_refinements")
    op.drop_index("ix_campaign_refinements_refinement_type", table_name="campaign_refinements")
    op.drop_index("ix_campaign_refinements_source_id", table_name="campaign_refinements")
    op.drop_index("ix_campaign_refinements_source_type", table_name="campaign_refinements")
    op.drop_index("ix_campaign_refinements_campaign_id", table_name="campaign_refinements")
    op.drop_table("campaign_refinements")
