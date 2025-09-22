"""Create payment service tables

Revision ID: 004_pagos_tables
Revises: 003_nullable_click
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_pagos_tables'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create pagos table
    op.create_table('pagos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('id_embajador', sa.String(length=255), nullable=False),
        sa.Column('id_partner', sa.String(length=255), nullable=False),
        sa.Column('id_conversion', sa.String(length=255), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('moneda', sa.String(length=10), nullable=False),
        sa.Column('estado', sa.String(length=50), nullable=False),
        sa.Column('tipo_pago', sa.String(length=50), nullable=False),
        sa.Column('metodo_pago', sa.String(length=50), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_procesamiento', sa.DateTime(), nullable=True),
        sa.Column('fecha_finalizacion', sa.DateTime(), nullable=True),
        sa.Column('motivo_fallo', sa.Text(), nullable=True),
        sa.Column('id_transaccion_externa', sa.String(length=255), nullable=True),
        sa.Column('metadatos', sa.JSON(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for pagos table
    op.create_index('ix_pagos_id_embajador', 'pagos', ['id_embajador'])
    op.create_index('ix_pagos_id_partner', 'pagos', ['id_partner'])
    op.create_index('ix_pagos_id_conversion', 'pagos', ['id_conversion'])
    op.create_index('ix_pagos_estado', 'pagos', ['estado'])
    op.create_index('ix_pagos_id_transaccion_externa', 'pagos', ['id_transaccion_externa'])
    
    # Create eventos_pago table (Event Sourcing)
    op.create_table('eventos_pago',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('id_pago', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_evento', sa.String(length=100), nullable=False),
        sa.Column('datos_evento', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('version_evento', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for eventos_pago table
    op.create_index('ix_eventos_pago_id_pago', 'eventos_pago', ['id_pago'])
    op.create_index('ix_eventos_pago_tipo_evento', 'eventos_pago', ['tipo_evento'])
    op.create_index('ix_eventos_pago_timestamp', 'eventos_pago', ['timestamp'])
    
    # Create outbox_pagos table (Outbox Pattern)
    op.create_table('outbox_pagos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evento_id', sa.String(length=255), nullable=False),
        sa.Column('evento_tipo', sa.String(length=100), nullable=False),
        sa.Column('evento_datos', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('publicado', sa.Boolean(), nullable=False),
        sa.Column('fecha_publicacion', sa.DateTime(), nullable=True),
        sa.Column('reintentos', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evento_id')
    )
    
    # Create indexes for outbox_pagos table
    op.create_index('ix_outbox_pagos_evento_id', 'outbox_pagos', ['evento_id'])
    op.create_index('ix_outbox_pagos_evento_tipo', 'outbox_pagos', ['evento_tipo'])
    op.create_index('ix_outbox_pagos_timestamp', 'outbox_pagos', ['timestamp'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_outbox_pagos_timestamp', table_name='outbox_pagos')
    op.drop_index('ix_outbox_pagos_evento_tipo', table_name='outbox_pagos')
    op.drop_index('ix_outbox_pagos_evento_id', table_name='outbox_pagos')
    op.drop_index('ix_eventos_pago_timestamp', table_name='eventos_pago')
    op.drop_index('ix_eventos_pago_tipo_evento', table_name='eventos_pago')
    op.drop_index('ix_eventos_pago_id_pago', table_name='eventos_pago')
    op.drop_index('ix_pagos_id_transaccion_externa', table_name='pagos')
    op.drop_index('ix_pagos_estado', table_name='pagos')
    op.drop_index('ix_pagos_id_conversion', table_name='pagos')
    op.drop_index('ix_pagos_id_partner', table_name='pagos')
    op.drop_index('ix_pagos_id_embajador', table_name='pagos')
    
    # Drop tables
    op.drop_table('outbox_pagos')
    op.drop_table('eventos_pago')
    op.drop_table('pagos')
