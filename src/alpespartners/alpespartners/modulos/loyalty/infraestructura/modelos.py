from sqlalchemy import Column, String, DateTime, Float, Integer
from datetime import datetime

from ....config.database import Base

class EmbajadorModel(Base):
    __tablename__ = "embajadores"

    id = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    estado = Column(String, default="PENDIENTE")  # PENDIENTE, ACTIVO, INACTIVO
    id_partner = Column(String, nullable=True, index=True)
    fecha_registro = Column(DateTime, default=datetime.now)
    
    # Métricas básicas
    total_referidos = Column(Integer, default=0)
    comisiones_ganadas = Column(Float, default=0.0)