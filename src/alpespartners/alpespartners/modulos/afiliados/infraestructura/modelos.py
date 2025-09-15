from sqlalchemy import Column, String, Float, DateTime, Text, Integer, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class AfiliadoModel(Base):
    """Modelo SQLAlchemy para afiliados"""
    __tablename__ = "afiliados"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo_afiliado = Column(String(50), nullable=False, unique=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    tipo_afiliado = Column(String(50), nullable=False, index=True)
    estado = Column(String(50), nullable=False, index=True)
    
    # Información de contacto
    email = Column(String(255), nullable=False, unique=True, index=True)
    telefono = Column(String(50), nullable=True)
    direccion = Column(Text, nullable=True)
    ciudad = Column(String(100), nullable=True, index=True)
    pais = Column(String(100), nullable=True, index=True)
    codigo_postal = Column(String(20), nullable=True)
    
    # Información fiscal
    tipo_documento = Column(String(50), nullable=False)
    numero_documento = Column(String(100), nullable=False, index=True)
    nombre_fiscal = Column(String(255), nullable=False)
    direccion_fiscal = Column(Text, nullable=True)
    
    # Configuración
    comision_porcentaje = Column(Float, nullable=False, default=5.0)
    limite_mensual = Column(Float, nullable=True)
    metodo_pago_preferido = Column(String(50), nullable=False, default="TRANSFERENCIA_BANCARIA")
    notificaciones_email = Column(Boolean, nullable=False, default=True)
    notificaciones_sms = Column(Boolean, nullable=False, default=False)
    
    # Metadatos
    fecha_registro = Column(DateTime, nullable=False, index=True)
    fecha_ultima_actividad = Column(DateTime, nullable=True, index=True)
    notas = Column(Text, nullable=True)
    metadatos = Column(JSON, nullable=True)
    version = Column(Integer, nullable=False, default=0)

class EventoOutboxModel(Base):
    """Modelo SQLAlchemy para outbox de eventos de afiliados"""
    __tablename__ = "eventos_outbox_afiliados"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_evento = Column(String(255), nullable=False, unique=True, index=True)
    tipo_evento = Column(String(100), nullable=False, index=True)
    id_agregado = Column(String(255), nullable=False, index=True)
    datos_evento = Column(JSON, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, index=True)
    fecha_procesamiento = Column(DateTime, nullable=True)
    procesado = Column(Boolean, nullable=False, default=False, index=True)
    intentos = Column(Integer, nullable=False, default=0)
    error = Column(Text, nullable=True)
