"""rename metadata to metadatos

Revision ID: 005_rename_metadata_to_metadatos
Revises: 004_pagos_tables
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_rename_metadata_to_metadatos'
down_revision = '004_pagos_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the metadata column exists before trying to rename it
    # This handles the case where the database was recreated and the column
    # was already created as 'metadatos' in the previous migration
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('pagos')]
    
    if 'metadata' in columns and 'metadatos' not in columns:
        # Only rename if metadata exists and metadatos doesn't exist
        op.alter_column('pagos', 'metadata', new_column_name='metadatos')
    # If metadatos already exists, do nothing (column was created correctly)


def downgrade():
    # Check if the metadatos column exists before trying to rename it back
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('pagos')]
    
    if 'metadatos' in columns and 'metadata' not in columns:
        # Only rename if metadatos exists and metadata doesn't exist
        op.alter_column('pagos', 'metadatos', new_column_name='metadata')
    # If metadata already exists, do nothing
