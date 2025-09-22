"""Create afiliados outbox table

Revision ID: 007_afiliados_outbox
Revises: 006_afiliados_tables
Create Date: 2024-01-15 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_afiliados_outbox'
down_revision = '006_afiliados_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create eventos_outbox_afiliados table
    op.create_table('eventos_outbox_afiliados',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('id_evento', sa.String(length=255), nullable=False),
        sa.Column('tipo_evento', sa.String(length=100), nullable=False),
        sa.Column('id_agregado', sa.String(length=255), nullable=False),
        sa.Column('datos_evento', sa.JSON(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_procesamiento', sa.DateTime(), nullable=True),
        sa.Column('procesado', sa.Boolean(), nullable=False),
        sa.Column('intentos', sa.Integer(), nullable=False),
        sa.Column('error', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for outbox table
    op.create_index('ix_eventos_outbox_afiliados_id_evento', 'eventos_outbox_afiliados', ['id_evento'], unique=True)
    op.create_index('ix_eventos_outbox_afiliados_tipo_evento', 'eventos_outbox_afiliados', ['tipo_evento'])
    op.create_index('ix_eventos_outbox_afiliados_id_agregado', 'eventos_outbox_afiliados', ['id_agregado'])
    op.create_index('ix_eventos_outbox_afiliados_fecha_creacion', 'eventos_outbox_afiliados', ['fecha_creacion'])
    op.create_index('ix_eventos_outbox_afiliados_procesado', 'eventos_outbox_afiliados', ['procesado'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_eventos_outbox_afiliados_procesado', table_name='eventos_outbox_afiliados')
    op.drop_index('ix_eventos_outbox_afiliados_fecha_creacion', table_name='eventos_outbox_afiliados')
    op.drop_index('ix_eventos_outbox_afiliados_id_agregado', table_name='eventos_outbox_afiliados')
    op.drop_index('ix_eventos_outbox_afiliados_tipo_evento', table_name='eventos_outbox_afiliados')
    op.drop_index('ix_eventos_outbox_afiliados_id_evento', table_name='eventos_outbox_afiliados')
    
    # Drop table
    op.drop_table('eventos_outbox_afiliados')
