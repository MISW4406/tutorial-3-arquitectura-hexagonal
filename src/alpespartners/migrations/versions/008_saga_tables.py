"""Saga tables

Revision ID: 008_saga_tables
Revises: 007_afiliados_outbox
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_saga_tables'
down_revision = '007_afiliados_outbox'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla de sagas
    op.create_table('sagas',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('estado', sa.String(20), nullable=False),
        sa.Column('datos_contexto', sa.JSON, nullable=True),
        sa.Column('timestamp_inicio', sa.DateTime, nullable=False),
        sa.Column('timestamp_fin', sa.DateTime, nullable=True),
        sa.Column('error_global', sa.Text, nullable=True)
    )
    
    # Crear tabla de pasos de saga
    op.create_table('pasos_saga',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('saga_id', sa.String(36), sa.ForeignKey('sagas.id'), nullable=False),
        sa.Column('orden', sa.Integer, nullable=False),
        sa.Column('servicio', sa.String(50), nullable=False),
        sa.Column('accion', sa.String(100), nullable=False),
        sa.Column('estado', sa.String(20), nullable=False),
        sa.Column('datos_entrada', sa.JSON, nullable=True),
        sa.Column('datos_salida', sa.JSON, nullable=True),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('timestamp_inicio', sa.DateTime, nullable=True),
        sa.Column('timestamp_fin', sa.DateTime, nullable=True)
    )
    
    # Crear tabla de compensaciones
    op.create_table('compensaciones_saga',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('paso_id', sa.String(36), sa.ForeignKey('pasos_saga.id'), nullable=False),
        sa.Column('servicio', sa.String(50), nullable=False),
        sa.Column('accion', sa.String(100), nullable=False),
        sa.Column('datos_compensacion', sa.JSON, nullable=True),
        sa.Column('exitoso', sa.Boolean, default=False),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False)
    )
    
    # Crear tabla de logs de saga
    op.create_table('saga_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('saga_id', sa.String(36), sa.ForeignKey('sagas.id'), nullable=False),
        sa.Column('evento', sa.String(100), nullable=False),
        sa.Column('datos_evento', sa.JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('nivel', sa.String(20), default='INFO')
    )
    
    # Crear índices para mejorar performance
    op.create_index('idx_sagas_estado', 'sagas', ['estado'])
    op.create_index('idx_sagas_tipo', 'sagas', ['tipo'])
    op.create_index('idx_sagas_timestamp', 'sagas', ['timestamp_inicio'])
    op.create_index('idx_pasos_saga_id', 'pasos_saga', ['saga_id'])
    op.create_index('idx_pasos_orden', 'pasos_saga', ['saga_id', 'orden'])
    op.create_index('idx_saga_logs_saga_id', 'saga_logs', ['saga_id'])
    op.create_index('idx_saga_logs_timestamp', 'saga_logs', ['timestamp'])


def downgrade():
    # Eliminar índices
    op.drop_index('idx_saga_logs_timestamp', 'saga_logs')
    op.drop_index('idx_saga_logs_saga_id', 'saga_logs')
    op.drop_index('idx_pasos_orden', 'pasos_saga')
    op.drop_index('idx_pasos_saga_id', 'pasos_saga')
    op.drop_index('idx_sagas_timestamp', 'sagas')
    op.drop_index('idx_sagas_tipo', 'sagas')
    op.drop_index('idx_sagas_estado', 'sagas')
    
    # Eliminar tablas
    op.drop_table('saga_logs')
    op.drop_table('compensaciones_saga')
    op.drop_table('pasos_saga')
    op.drop_table('sagas')

