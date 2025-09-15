from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

class EstadoPago(Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    PROCESADO = "PROCESADO"
    FALLIDO = "FALLIDO"
    REVERTIDO = "REVERTIDO"

@dataclass
class QueryObtenerPago:
    """Query para obtener un pago por ID"""
    id_pago: str

@dataclass
class QueryObtenerPagosEmbajador:
    """Query para obtener pagos de un embajador"""
    id_embajador: str
    estado: Optional[EstadoPago] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limite: int = 100
    offset: int = 0

@dataclass
class QueryObtenerPagosPartner:
    """Query para obtener pagos de un partner"""
    id_partner: str
    estado: Optional[EstadoPago] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limite: int = 100
    offset: int = 0

@dataclass
class QueryObtenerPagosPendientes:
    """Query para obtener pagos pendientes de procesamiento"""
    limite: int = 50
    offset: int = 0

@dataclass
class QueryObtenerEstadisticasPagos:
    """Query para obtener estadísticas de pagos"""
    id_embajador: Optional[str] = None
    id_partner: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None

@dataclass
class QueryObtenerEventosPago:
    """Query para obtener eventos de un pago (Event Sourcing)"""
    id_pago: str
    tipo_evento: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
