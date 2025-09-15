from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict
from datetime import datetime

class TipoConversion(Enum):
    VENTA = "VENTA"
    REGISTRO = "REGISTRO"
    LEAD = "LEAD"
    INSTALACION = "INSTALACION"
    SUSCRIPCION = "SUSCRIPCION"

class ModeloAtribucion(Enum):
    ULTIMO_CLICK = "ULTIMO_CLICK"
    PRIMER_CLICK = "PRIMER_CLICK"
    LINEAL = "LINEAL"
    PONDERADO = "PONDERADO"

@dataclass(frozen=True)
class MetadataCliente:
    user_agent: str
    ip_address: str
    referrer: Optional[str]
    device_info: Dict
    location_info: Optional[Dict]

@dataclass(frozen=True)
class InformacionMonetaria:
    valor: float
    moneda: str
    comision: float
    porcentaje_comision: float

@dataclass(frozen=True)
class DatosAtribucion:
    modelo: ModeloAtribucion
    porcentaje: float
    timestamp: datetime
    ventana_atribucion: int  # en días

