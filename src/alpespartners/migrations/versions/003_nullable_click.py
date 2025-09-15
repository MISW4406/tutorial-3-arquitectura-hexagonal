"""
Migración para hacer el id_click nullable en conversiones
src/alpespartners/migrations/versions/003_nullable_click.py
"""

"""Make id_click nullable in conversiones

Revision ID: 003
Revises: 002
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Hacer id_click nullable y remover la foreign key constraint
    op.drop_constraint('conversiones_id_click_fkey', 'conversiones', type_='foreignkey')
    op.alter_column('conversiones', 'id_click', nullable=True)
    
    # Opcional: volver a crear la foreign key pero con nullable
    op.create_foreign_key(
        'conversiones_id_click_fkey', 
        'conversiones', 
        'clicks', 
        ['id_click'], 
        ['id'], 
        ondelete='SET NULL'
    )

def downgrade() -> None:
    op.drop_constraint('conversiones_id_click_fkey', 'conversiones', type_='foreignkey')
    op.alter_column('conversiones', 'id_click', nullable=False)
    op.create_foreign_key(
        'conversiones_id_click_fkey', 
        'conversiones', 
        'clicks', 
        ['id_click'], 
        ['id']
    )