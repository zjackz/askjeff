"""add api import fields

Revision ID: 0010
Revises: 0009
Create Date: 2025-12-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('import_batches', sa.Column('source_type', sa.String(length=20), server_default='file', nullable=True))
    op.add_column('import_batches', sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

def downgrade() -> None:
    op.drop_column('import_batches', 'metadata')
    op.drop_column('import_batches', 'source_type')
