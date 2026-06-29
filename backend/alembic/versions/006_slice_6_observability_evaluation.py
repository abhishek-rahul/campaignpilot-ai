"""create slice 6 evaluation results table

Revision ID: 006_slice_6
Revises: 005_slice_5
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006_slice_6"
down_revision: str | None = "005_slice_5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "evaluation_results",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("variant_id", sa.String(length=50), sa.ForeignKey("message_variants.id"), nullable=True),
        sa.Column("evaluation_type", sa.String(length=50), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("grade", sa.String(length=5), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("checks_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_evaluation_results_campaign_id", "evaluation_results", ["campaign_id"])
    op.create_index("ix_evaluation_results_variant_id", "evaluation_results", ["variant_id"])
    op.create_index("ix_evaluation_results_evaluation_type", "evaluation_results", ["evaluation_type"])
    op.create_index("ix_evaluation_results_grade", "evaluation_results", ["grade"])
    op.create_index("ix_evaluation_results_passed", "evaluation_results", ["passed"])
    op.create_index("ix_evaluation_results_created_at", "evaluation_results", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_evaluation_results_created_at", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_passed", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_grade", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_evaluation_type", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_variant_id", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_campaign_id", table_name="evaluation_results")
    op.drop_table("evaluation_results")
