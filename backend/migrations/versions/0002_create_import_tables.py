"""create import related tables

Revision ID: 0002
Revises: 0001
Create Date: 2025-11-15
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=True),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("import_strategy", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("success_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("failure_summary", sa.JSON(), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "product_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("batch_id", sa.String(length=36), sa.ForeignKey("import_batches.id"), nullable=False),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("sales_rank", sa.Integer(), nullable=True),
        sa.Column("reviews", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("normalized_payload", sa.JSON(), nullable=True),
        sa.Column("validation_status", sa.String(length=32), nullable=False, server_default="valid"),
        sa.Column("validation_messages", sa.JSON(), nullable=True),
        sa.Column("ingested_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "idx_product_batch_asin",
        "product_records",
        ["batch_id", "asin"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("idx_product_batch_asin", table_name="product_records")
    op.drop_table("product_records")
    op.drop_table("import_batches")
