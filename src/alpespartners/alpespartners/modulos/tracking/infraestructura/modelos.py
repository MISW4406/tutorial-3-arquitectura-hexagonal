from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship

from ....config.database import Base

class ClickModel(Base):
    __tablename__ = "clicks"

    id = Column(String, primary_key=True, index=True)
    id_partner = Column(String, index=True)
    id_campana = Column(String, index=True)
    url_origen = Column(String)
    url_destino = Column(String)
    timestamp = Column(DateTime)
    metadata_cliente = Column(JSON)
    total_conversiones = Column(Integer, default=0)
    valor_total = Column(Float, default=0.0)
    comision_total = Column(Float, default=0.0)

    conversiones = relationship("ConversionModel", back_populates="click")

class ConversionModel(Base):
    __tablename__ = "conversiones"

    id = Column(String, primary_key=True, index=True)
    id_click = Column(String, ForeignKey("clicks.id"), nullable=True)
    id_partner = Column(String, index=True)
    id_campana = Column(String, index=True)
    tipo = Column(String)
    timestamp = Column(DateTime)
    metadata_cliente = Column(JSON)
    
    # Información monetaria
    valor = Column(Float)
    moneda = Column(String)
    comision = Column(Float)
    porcentaje_comision = Column(Float)

    click = relationship("ClickModel", back_populates="conversiones")
    atribuciones = relationship("AtribucionModel", back_populates="conversion")

class AtribucionModel(Base):
    __tablename__ = "atribuciones"

    id = Column(String, primary_key=True, index=True)
    id_conversion = Column(String, ForeignKey("conversiones.id"))
    modelo = Column(String)
    porcentaje = Column(Float)
    timestamp = Column(DateTime)
    ventana_atribucion = Column(Integer)  # en días

    conversion = relationship("ConversionModel", back_populates="atribuciones")