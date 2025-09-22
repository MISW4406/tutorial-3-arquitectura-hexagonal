from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

@dataclass
class ComandoCrearPago:
    """Comando para crear un nuevo pago de comisión"""
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto: float
    moneda: str
    metodo_pago: str
    datos_beneficiario: Dict[str, Any]
    referencia: str
    descripcion: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ComandoProcesarPago:
    """Comando para procesar un pago existente"""
    id_pago: str
    id_transaccion_externa: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ComandoRevertirPago:
    """Comando para revertir un pago"""
    id_pago: str
    motivo_reversion: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ComandoMarcarPagoFallido:
    """Comando para marcar un pago como fallido"""
    id_pago: str
    motivo_fallo: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ComandoValidarPago:
    """Comando para validar un pago antes de procesarlo"""
    id_pago: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
