"""convert string ids to uuid

Revision ID: 0007
Revises: 0006
Create Date: 2025-11-18
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # audit_logs
    op.execute("ALTER TABLE audit_logs ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute("ALTER TABLE audit_logs ALTER COLUMN actor_id TYPE uuid USING actor_id::uuid")
    op.execute("ALTER TABLE audit_logs ALTER COLUMN entity_id TYPE uuid USING entity_id::uuid")

    # query_sessions
    op.execute("ALTER TABLE query_sessions ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute("ALTER TABLE query_sessions ALTER COLUMN asked_by TYPE uuid USING asked_by::uuid")

    # import / product
    op.execute("ALTER TABLE product_records DROP CONSTRAINT product_records_batch_id_fkey")
    op.execute("ALTER TABLE import_batches ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute("ALTER TABLE import_batches ALTER COLUMN created_by TYPE uuid USING created_by::uuid")
    op.execute("ALTER TABLE product_records ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute("ALTER TABLE product_records ALTER COLUMN batch_id TYPE uuid USING batch_id::uuid")
    op.execute(
        "ALTER TABLE product_records ADD CONSTRAINT product_records_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES import_batches(id)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE product_records DROP CONSTRAINT product_records_batch_id_fkey")
    op.execute("ALTER TABLE product_records ALTER COLUMN batch_id TYPE varchar(36) USING batch_id::text")
    op.execute("ALTER TABLE product_records ALTER COLUMN id TYPE varchar(36) USING id::text")
    op.execute("ALTER TABLE import_batches ALTER COLUMN created_by TYPE varchar(36) USING created_by::text")
    op.execute("ALTER TABLE import_batches ALTER COLUMN id TYPE varchar(36) USING id::text")
    op.execute(
        "ALTER TABLE product_records ADD CONSTRAINT product_records_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES import_batches(id)"
    )

    op.execute("ALTER TABLE query_sessions ALTER COLUMN asked_by TYPE varchar(36) USING asked_by::text")
    op.execute("ALTER TABLE query_sessions ALTER COLUMN id TYPE varchar(36) USING id::text")

    op.execute("ALTER TABLE audit_logs ALTER COLUMN entity_id TYPE varchar(36) USING entity_id::text")
    op.execute("ALTER TABLE audit_logs ALTER COLUMN actor_id TYPE varchar(36) USING actor_id::text")
    op.execute("ALTER TABLE audit_logs ALTER COLUMN id TYPE varchar(36) USING id::text")
