from sqlalchemy import Column, String, Float, DateTime, Text, Integer, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class PagoModel(Base):
    """Modelo SQLAlchemy para pagos"""
    __tablename__ = "pagos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_embajador = Column(String(255), nullable=False, index=True)
    id_partner = Column(String(255), nullable=False, index=True)
    id_conversion = Column(String(255), nullable=False, index=True)
    monto = Column(Float, nullable=False)
    moneda = Column(String(10), nullable=False, default="USD")
    estado = Column(String(50), nullable=False, index=True)
    tipo_pago = Column(String(50), nullable=False)
    metodo_pago = Column(String(50), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_procesamiento = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    motivo_fallo = Column(Text, nullable=True)
    id_transaccion_externa = Column(String(255), nullable=True, index=True)
    metadatos = Column(JSON, nullable=True)
    version = Column(Integer, nullable=False, default=0)

class EventoPagoModel(Base):
    """Modelo SQLAlchemy para eventos de pago (Event Sourcing)"""
    __tablename__ = "eventos_pago"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_pago = Column(UUID(as_uuid=True), nullable=False, index=True)
    tipo_evento = Column(String(100), nullable=False, index=True)
    datos_evento = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    version_evento = Column(Integer, nullable=False, default=1)

class OutboxModel(Base):
    """Modelo SQLAlchemy para patrón Outbox"""
    __tablename__ = "outbox_pagos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evento_id = Column(String(255), nullable=False, unique=True, index=True)
    evento_tipo = Column(String(100), nullable=False, index=True)
    evento_datos = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    publicado = Column(Boolean, nullable=False, default=False)
    fecha_publicacion = Column(DateTime, nullable=True)
    reintentos = Column(Integer, nullable=False, default=0)
