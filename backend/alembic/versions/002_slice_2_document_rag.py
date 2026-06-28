"""create slice 2 document rag tables

Revision ID: 002_slice_2
Revises: 001_slice_1
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_slice_2"
down_revision: str | None = "001_slice_1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "brand_documents",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=True),
        sa.Column("uploaded_by", sa.String(length=50), sa.ForeignKey("campaign_managers.id"), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="UPLOADED"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_brand_documents_campaign_id", "brand_documents", ["campaign_id"])
    op.create_index("ix_brand_documents_status", "brand_documents", ["status"])
    op.create_index("ix_brand_documents_document_type", "brand_documents", ["document_type"])
    op.create_index("ix_brand_documents_created_at", "brand_documents", ["created_at"])

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("document_id", sa.String(length=50), sa.ForeignKey("brand_documents.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("elasticsearch_doc_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_document_chunks_chunk_index", "document_chunks", ["document_id", "chunk_index"])

    op.create_table(
        "embedding_records",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("document_id", sa.String(length=50), sa.ForeignKey("brand_documents.id"), nullable=False),
        sa.Column("chunk_id", sa.String(length=50), sa.ForeignKey("document_chunks.id"), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("vector_dimension", sa.Integer(), nullable=False),
        sa.Column("elasticsearch_index", sa.String(length=150), nullable=False),
        sa.Column("elasticsearch_document_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="INDEXED"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_embedding_records_document_id", "embedding_records", ["document_id"])
    op.create_index("ix_embedding_records_chunk_id", "embedding_records", ["chunk_id"])
    op.create_index("ix_embedding_records_status", "embedding_records", ["status"])

    op.create_table(
        "retrieved_contexts",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("campaign_id", sa.String(length=50), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("document_id", sa.String(length=50), sa.ForeignKey("brand_documents.id"), nullable=True),
        sa.Column("chunk_id", sa.String(length=50), sa.ForeignKey("document_chunks.id"), nullable=True),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("retrieved_text", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("rank_position", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False, server_default="document_chunk"),
        sa.Column("used_for", sa.String(length=50), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_retrieved_contexts_campaign_id", "retrieved_contexts", ["campaign_id"])
    op.create_index("ix_retrieved_contexts_used_for", "retrieved_contexts", ["used_for"])
    op.create_index("ix_retrieved_contexts_created_at", "retrieved_contexts", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_retrieved_contexts_created_at", table_name="retrieved_contexts")
    op.drop_index("ix_retrieved_contexts_used_for", table_name="retrieved_contexts")
    op.drop_index("ix_retrieved_contexts_campaign_id", table_name="retrieved_contexts")
    op.drop_table("retrieved_contexts")
    op.drop_index("ix_embedding_records_status", table_name="embedding_records")
    op.drop_index("ix_embedding_records_chunk_id", table_name="embedding_records")
    op.drop_index("ix_embedding_records_document_id", table_name="embedding_records")
    op.drop_table("embedding_records")
    op.drop_index("ix_document_chunks_chunk_index", table_name="document_chunks")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_brand_documents_created_at", table_name="brand_documents")
    op.drop_index("ix_brand_documents_document_type", table_name="brand_documents")
    op.drop_index("ix_brand_documents_status", table_name="brand_documents")
    op.drop_index("ix_brand_documents_campaign_id", table_name="brand_documents")
    op.drop_table("brand_documents")
