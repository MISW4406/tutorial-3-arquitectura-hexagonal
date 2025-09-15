"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clicks table
    op.create_table('clicks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('id_partner', sa.String(), nullable=True),
        sa.Column('id_campana', sa.String(), nullable=True),
        sa.Column('url_origen', sa.String(), nullable=True),
        sa.Column('url_destino', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('metadata_cliente', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clicks_id'), 'clicks', ['id'], unique=False)
    op.create_index(op.f('ix_clicks_id_campana'), 'clicks', ['id_campana'], unique=False)
    op.create_index(op.f('ix_clicks_id_partner'), 'clicks', ['id_partner'], unique=False)

    # Create conversiones table
    op.create_table('conversiones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('id_click', sa.String(), nullable=True),
        sa.Column('id_partner', sa.String(), nullable=True),
        sa.Column('id_campana', sa.String(), nullable=True),
        sa.Column('tipo', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('metadata_cliente', sa.JSON(), nullable=True),
        sa.Column('valor', sa.Float(), nullable=True),
        sa.Column('moneda', sa.String(), nullable=True),
        sa.Column('comision', sa.Float(), nullable=True),
        sa.Column('porcentaje_comision', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['id_click'], ['clicks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversiones_id'), 'conversiones', ['id'], unique=False)
    op.create_index(op.f('ix_conversiones_id_campana'), 'conversiones', ['id_campana'], unique=False)
    op.create_index(op.f('ix_conversiones_id_partner'), 'conversiones', ['id_partner'], unique=False)

    # Create atribuciones table
    op.create_table('atribuciones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('id_conversion', sa.String(), nullable=True),
        sa.Column('modelo', sa.String(), nullable=True),
        sa.Column('porcentaje', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('ventana_atribucion', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_conversion'], ['conversiones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('atribuciones')
    op.drop_table('conversiones')
    op.drop_table('clicks')
