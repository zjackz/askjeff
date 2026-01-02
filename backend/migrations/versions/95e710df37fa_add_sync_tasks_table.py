"""add_sync_tasks_table

Revision ID: 95e710df37fa
Revises: 0011
Create Date: 2025-12-31 02:32:37.582645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95e710df37fa'
down_revision: Union[str, None] = '0011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('sync_tasks',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('sync_type', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('records_synced', sa.Integer(), nullable=False),
    sa.Column('records_failed', sa.Integer(), nullable=False),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['store_id'], ['amazon_stores.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sync_tasks_store_id'), 'sync_tasks', ['store_id'], unique=False)
    op.create_index(op.f('ix_sync_tasks_sync_type'), 'sync_tasks', ['sync_type'], unique=False)
    op.create_index(op.f('ix_sync_tasks_status'), 'sync_tasks', ['status'], unique=False)
    op.create_index(op.f('ix_sync_tasks_created_at'), 'sync_tasks', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sync_tasks_created_at'), table_name='sync_tasks')
    op.drop_index(op.f('ix_sync_tasks_status'), table_name='sync_tasks')
    op.drop_index(op.f('ix_sync_tasks_sync_type'), table_name='sync_tasks')
    op.drop_index(op.f('ix_sync_tasks_store_id'), table_name='sync_tasks')
    op.drop_table('sync_tasks')
