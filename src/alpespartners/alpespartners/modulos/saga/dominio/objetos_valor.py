from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

class EstadoSaga(Enum):
    """Estados posibles de una saga"""
    INICIADA = "INICIADA"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"
    COMPENSANDO = "COMPENSANDO"
    COMPENSADA = "COMPENSADA"
    FALLIDA = "FALLIDA"
    TIMEOUT = "TIMEOUT"

class TipoSaga(Enum):
    """Tipos de saga disponibles"""
    PROCESAMIENTO_CONVERSION = "PROCESAMIENTO_CONVERSION"
    REGISTRO_AFILIADO_COMPLETO = "REGISTRO_AFILIADO_COMPLETO"
    PAGO_COMISION_COMPLETO = "PAGO_COMISION_COMPLETO"

class EstadoPaso(Enum):
    """Estados de un paso individual en la saga"""
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADO = "COMPLETADO"
    FALLIDO = "FALLIDO"
    COMPENSADO = "COMPENSADO"

@dataclass
class DatosPaso:
    """Datos específicos de un paso de la saga"""
    servicio: str
    accion: str
    datos_entrada: Dict[str, Any]
    datos_salida: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp_inicio: Optional[datetime] = None
    timestamp_fin: Optional[datetime] = None

@dataclass
class PasoCompensacion:
    """Información para compensar un paso"""
    servicio: str
    accion: str
    datos_compensacion: Dict[str, Any]
    exitoso: bool = False
    error: Optional[str] = None
    timestamp: Optional[datetime] = None

