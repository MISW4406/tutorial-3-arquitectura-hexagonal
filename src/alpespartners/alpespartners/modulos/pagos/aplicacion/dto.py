from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class EstadoPago(Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    PROCESADO = "PROCESADO"
    FALLIDO = "FALLIDO"
    REVERTIDO = "REVERTIDO"

class TipoPago(Enum):
    COMISION = "COMISION"
    BONIFICACION = "BONIFICACION"
    REEMBOLSO = "REEMBOLSO"

class MetodoPago(Enum):
    TRANSFERENCIA_BANCARIA = "TRANSFERENCIA_BANCARIA"
    PAYPAL = "PAYPAL"
    STRIPE = "STRIPE"
    WISE = "WISE"

@dataclass
class PagoDTO:
    """DTO para representar un pago"""
    id_pago: str
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto: float
    moneda: str
    estado: EstadoPago
    tipo_pago: TipoPago
    metodo_pago: MetodoPago
    fecha_creacion: datetime
    fecha_procesamiento: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    motivo_fallo: Optional[str] = None
    id_transaccion_externa: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class InformacionPagoDTO:
    """DTO para información de pago"""
    metodo_pago: MetodoPago
    datos_beneficiario: Dict[str, Any]
    referencia: str
    descripcion: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class DetalleComisionDTO:
    """DTO para detalles de comisión"""
    id_conversion: str
    id_click: Optional[str]
    id_campana: str
    valor_conversion: float
    porcentaje_comision: float
    monto_comision: float
    modelo_atribucion: str
    fecha_conversion: datetime
    metadata_conversion: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata_conversion is None:
            self.metadata_conversion = {}

@dataclass
class ResultadoPagoDTO:
    """DTO para resultado de pago"""
    exitoso: bool
    id_transaccion_externa: Optional[str]
    mensaje: str
    codigo_error: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class EstadisticasPagosDTO:
    """DTO para estadísticas de pagos"""
    total_pagos: int
    total_monto: float
    pagos_exitosos: int
    pagos_fallidos: int
    pagos_pendientes: int
    monto_promedio: float
    tasa_exito: float
    pagos_por_estado: Dict[str, int]
    pagos_por_tipo: Dict[str, int]
    pagos_por_metodo: Dict[str, int]
    periodo_desde: datetime
    periodo_hasta: datetime

@dataclass
class EventoPagoDTO:
    """DTO para eventos de pago (Event Sourcing)"""
    id_evento: str
    id_pago: str
    tipo_evento: str
    datos_evento: Dict[str, Any]
    timestamp: datetime
    version_evento: int
