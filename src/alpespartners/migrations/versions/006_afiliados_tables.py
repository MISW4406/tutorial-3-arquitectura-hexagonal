"""Create afiliados tables

Revision ID: 006_afiliados_tables
Revises: 005_rename_metadata_to_metadatos
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_afiliados_tables'
down_revision = '005_rename_metadata_to_metadatos'
branch_labels = None
depends_on = None


def upgrade():
    # Create afiliados table
    op.create_table('afiliados',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('codigo_afiliado', sa.String(length=50), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('tipo_afiliado', sa.String(length=50), nullable=False),
        sa.Column('estado', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('telefono', sa.String(length=50), nullable=True),
        sa.Column('direccion', sa.Text(), nullable=True),
        sa.Column('ciudad', sa.String(length=100), nullable=True),
        sa.Column('pais', sa.String(length=100), nullable=True),
        sa.Column('codigo_postal', sa.String(length=20), nullable=True),
        sa.Column('tipo_documento', sa.String(length=50), nullable=False),
        sa.Column('numero_documento', sa.String(length=100), nullable=False),
        sa.Column('nombre_fiscal', sa.String(length=255), nullable=False),
        sa.Column('direccion_fiscal', sa.Text(), nullable=True),
        sa.Column('comision_porcentaje', sa.Float(), nullable=False),
        sa.Column('limite_mensual', sa.Float(), nullable=True),
        sa.Column('metodo_pago_preferido', sa.String(length=50), nullable=False),
        sa.Column('notificaciones_email', sa.Boolean(), nullable=False),
        sa.Column('notificaciones_sms', sa.Boolean(), nullable=False),
        sa.Column('fecha_registro', sa.DateTime(), nullable=False),
        sa.Column('fecha_ultima_actividad', sa.DateTime(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('metadatos', sa.JSON(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for afiliados table
    op.create_index('ix_afiliados_codigo_afiliado', 'afiliados', ['codigo_afiliado'], unique=True)
    op.create_index('ix_afiliados_nombre', 'afiliados', ['nombre'])
    op.create_index('ix_afiliados_tipo_afiliado', 'afiliados', ['tipo_afiliado'])
    op.create_index('ix_afiliados_estado', 'afiliados', ['estado'])
    op.create_index('ix_afiliados_email', 'afiliados', ['email'], unique=True)
    op.create_index('ix_afiliados_ciudad', 'afiliados', ['ciudad'])
    op.create_index('ix_afiliados_pais', 'afiliados', ['pais'])
    op.create_index('ix_afiliados_numero_documento', 'afiliados', ['numero_documento'])
    op.create_index('ix_afiliados_fecha_registro', 'afiliados', ['fecha_registro'])
    op.create_index('ix_afiliados_fecha_ultima_actividad', 'afiliados', ['fecha_ultima_actividad'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_afiliados_fecha_ultima_actividad', table_name='afiliados')
    op.drop_index('ix_afiliados_fecha_registro', table_name='afiliados')
    op.drop_index('ix_afiliados_numero_documento', table_name='afiliados')
    op.drop_index('ix_afiliados_pais', table_name='afiliados')
    op.drop_index('ix_afiliados_ciudad', table_name='afiliados')
    op.drop_index('ix_afiliados_email', table_name='afiliados')
    op.drop_index('ix_afiliados_estado', table_name='afiliados')
    op.drop_index('ix_afiliados_tipo_afiliado', table_name='afiliados')
    op.drop_index('ix_afiliados_nombre', table_name='afiliados')
    op.drop_index('ix_afiliados_codigo_afiliado', table_name='afiliados')
    
    # Drop table
    op.drop_table('afiliados')
