from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

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
class InformacionPago:
    """Información necesaria para procesar el pago"""
    metodo_pago: MetodoPago
    datos_beneficiario: Dict[str, Any]  # Datos del embajador para recibir el pago
    referencia: str
    descripcion: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class DetalleComision:
    """Detalles específicos de la comisión"""
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
class ResultadoPago:
    """Resultado del procesamiento de pago"""
    exitoso: bool
    id_transaccion_externa: Optional[str]
    mensaje: str
    codigo_error: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ConfiguracionPago:
    """Configuración para el procesamiento de pagos"""
    metodo_pago_por_defecto: MetodoPago
    monto_minimo: float
    monto_maximo: float
    moneda_por_defecto: str
    timeout_segundos: int
    reintentos_maximos: int
    habilitado: bool = True

@dataclass
class MetadataPago:
    """Metadata adicional para el pago"""
    id_sesion: Optional[str] = None
    ip_cliente: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    custom_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_data is None:
            self.custom_data = {}
