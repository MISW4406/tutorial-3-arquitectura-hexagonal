"""Add loyalty tables

Revision ID: 002
Revises: 001
Create Date: 2024-03-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Crear tabla embajadores
    op.create_table('embajadores',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('estado', sa.String(), nullable=False, server_default='PENDIENTE'),
        sa.Column('id_partner', sa.String(), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('total_referidos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comisiones_ganadas', sa.Float(), nullable=False, server_default='0.0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para optimizar consultas
    op.create_index(op.f('ix_embajadores_id'), 'embajadores', ['id'], unique=False)
    op.create_index(op.f('ix_embajadores_email'), 'embajadores', ['email'], unique=True)
    op.create_index(op.f('ix_embajadores_id_partner'), 'embajadores', ['id_partner'], unique=False)
    op.create_index(op.f('ix_embajadores_estado'), 'embajadores', ['estado'], unique=False)

def downgrade() -> None: 
    op.drop_index(op.f('ix_embajadores_estado'), 'embajadores')
    op.drop_index(op.f('ix_embajadores_id_partner'), 'embajadores')
    op.drop_index(op.f('ix_embajadores_email'), 'embajadores')
    op.drop_index(op.f('ix_embajadores_id'), 'embajadores')
    
    op.drop_table('embajadores')