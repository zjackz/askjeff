"""change import_batch id to integer

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-02 14:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Add new_batch_id to product_records
    op.add_column('product_records', sa.Column('new_batch_id', sa.Integer(), nullable=True))
    
    # 2. Populate new_batch_id based on join with import_batches
    # We use the existing UUID relationship to find the corresponding sequence_id
    op.execute("""
        UPDATE product_records pr
        SET new_batch_id = ib.sequence_id
        FROM import_batches ib
        WHERE pr.batch_id = ib.id
    """)
    
    # 3. Drop constraints referencing the old UUID id
    # We need to find the constraint name first, but usually it's predictable or we can drop by column
    # Dropping foreign key from product_records
    op.drop_constraint('product_records_batch_id_fkey', 'product_records', type_='foreignkey')
    
    # Drop index on product_records (batch_id, asin)
    op.drop_index('idx_product_batch_asin', table_name='product_records')
    
    # 4. Modify import_batches
    # Drop primary key constraint
    op.execute("ALTER TABLE import_batches DROP CONSTRAINT import_batches_pkey CASCADE")
    
    # Drop the old UUID id column
    op.drop_column('import_batches', 'id')
    
    # Rename sequence_id to id
    op.alter_column('import_batches', 'sequence_id', new_column_name='id')
    
    # Make new id the primary key
    op.create_primary_key('import_batches_pkey', 'import_batches', ['id'])
    
    # 5. Modify product_records
    # Drop old batch_id column
    op.drop_column('product_records', 'batch_id')
    
    # Rename new_batch_id to batch_id
    op.alter_column('product_records', 'new_batch_id', new_column_name='batch_id')
    
    # Set not null
    op.alter_column('product_records', 'batch_id', nullable=False)
    
    # Create foreign key
    op.create_foreign_key(
        'product_records_batch_id_fkey',
        'product_records',
        'import_batches',
        ['batch_id'],
        ['id']
    )
    
    # Re-create index
    op.create_index(
        'idx_product_batch_asin',
        'product_records',
        ['batch_id', 'asin'],
        unique=True
    )

def downgrade():
    # This is a complex downgrade, simplified for now as we don't expect to revert easily without data loss or complex logic
    # Ideally we would reverse the steps: add UUID columns, populate them, switch PKs.
    pass
