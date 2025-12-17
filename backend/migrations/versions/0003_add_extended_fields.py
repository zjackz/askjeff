"""add extended_data and data_source to product_record

Revision ID: 0003
Revises: 0002
Create Date: 2025-12-17 20:35:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 extended_data 字段（JSON 类型）
    op.add_column('product_records', sa.Column('extended_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # 添加 data_source 字段（String 类型，默认 'file'）
    op.add_column('product_records', sa.Column('data_source', sa.String(length=20), nullable=False, server_default='file'))


def downgrade() -> None:
    # 删除字段
    op.drop_column('product_records', 'data_source')
    op.drop_column('product_records', 'extended_data')
