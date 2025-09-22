from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class SagaModel(Base):
    """Modelo SQLAlchemy para sagas"""
    __tablename__ = "sagas"
    
    id = Column(String(36), primary_key=True)
    tipo = Column(String(50), nullable=False)
    estado = Column(String(20), nullable=False)
    datos_contexto = Column(JSON, nullable=True)
    timestamp_inicio = Column(DateTime, nullable=False, default=datetime.now)
    timestamp_fin = Column(DateTime, nullable=True)
    error_global = Column(Text, nullable=True)
    
    # Relación con pasos
    pasos = relationship("PasoModel", back_populates="saga", cascade="all, delete-orphan")
    logs = relationship("SagaLogModel", back_populates="saga", cascade="all, delete-orphan")

class PasoModel(Base):
    """Modelo SQLAlchemy para pasos de saga"""
    __tablename__ = "pasos_saga"
    
    id = Column(String(36), primary_key=True)
    saga_id = Column(String(36), ForeignKey("sagas.id"), nullable=False)
    orden = Column(Integer, nullable=False)
    servicio = Column(String(50), nullable=False)
    accion = Column(String(100), nullable=False)
    estado = Column(String(20), nullable=False)
    datos_entrada = Column(JSON, nullable=True)
    datos_salida = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    timestamp_inicio = Column(DateTime, nullable=True)
    timestamp_fin = Column(DateTime, nullable=True)
    
    # Relación con saga
    saga = relationship("SagaModel", back_populates="pasos")

class CompensacionModel(Base):
    """Modelo SQLAlchemy para compensaciones de saga"""
    __tablename__ = "compensaciones_saga"
    
    id = Column(String(36), primary_key=True)
    paso_id = Column(String(36), ForeignKey("pasos_saga.id"), nullable=False)
    servicio = Column(String(50), nullable=False)
    accion = Column(String(100), nullable=False)
    datos_compensacion = Column(JSON, nullable=True)
    exitoso = Column(Boolean, default=False)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)

class SagaLogModel(Base):
    """Modelo SQLAlchemy para el log de sagas"""
    __tablename__ = "saga_logs"
    
    id = Column(String(36), primary_key=True)
    saga_id = Column(String(36), ForeignKey("sagas.id"), nullable=False)
    evento = Column(String(100), nullable=False)
    datos_evento = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    nivel = Column(String(20), default="INFO")  # INFO, WARNING, ERROR
    
    # Relación con saga
    saga = relationship("SagaModel", back_populates="logs")

