from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from ....seedwork.dominio.eventos import EventoDominio

@dataclass
class PagoIniciado(EventoDominio):
    """Evento disparado cuando se inicia un pago de comisión"""
    id_pago: str
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto: float
    moneda: str
    tipo_pago: str
    informacion_pago: Dict
    detalle_comision: Dict
    timestamp: datetime
    
    def __init__(self, id_pago: str, id_embajador: str, id_partner: str, 
                 id_conversion: str, monto: float, moneda: str, tipo_pago: str,
                 informacion_pago: Dict, detalle_comision: Dict, timestamp: datetime):
        super().__init__()
        self.id_pago = id_pago
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.id_conversion = id_conversion
        self.monto = monto
        self.moneda = moneda
        self.tipo_pago = tipo_pago
        self.informacion_pago = informacion_pago
        self.detalle_comision = detalle_comision
        self.timestamp = timestamp

@dataclass
class PagoProcesado(EventoDominio):
    """Evento disparado cuando un pago se procesa exitosamente"""
    id_pago: str
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto: float
    moneda: str
    id_transaccion_externa: str
    timestamp: datetime
    
    def __init__(self, id_pago: str, id_embajador: str, id_partner: str, 
                 id_conversion: str, monto: float, moneda: str, 
                 id_transaccion_externa: str, timestamp: datetime):
        super().__init__()
        self.id_pago = id_pago
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.id_conversion = id_conversion
        self.monto = monto
        self.moneda = moneda
        self.id_transaccion_externa = id_transaccion_externa
        self.timestamp = timestamp

@dataclass
class PagoFallido(EventoDominio):
    """Evento disparado cuando un pago falla"""
    id_pago: str
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto: float
    moneda: str
    motivo_fallo: str
    timestamp: datetime
    
    def __init__(self, id_pago: str, id_embajador: str, id_partner: str, 
                 id_conversion: str, monto: float, moneda: str, 
                 motivo_fallo: str, timestamp: datetime):
        super().__init__()
        self.id_pago = id_pago
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.id_conversion = id_conversion
        self.monto = monto
        self.moneda = moneda
        self.motivo_fallo = motivo_fallo
        self.timestamp = timestamp

@dataclass
class ComisionPagada(EventoDominio):
    """Evento disparado cuando una comisión se paga exitosamente"""
    id_pago: str
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto_comision: float
    moneda: str
    id_transaccion_externa: str
    timestamp: datetime
    
    def __init__(self, id_pago: str, id_embajador: str, id_partner: str, 
                 id_conversion: str, monto_comision: float, moneda: str, 
                 id_transaccion_externa: str, timestamp: datetime):
        super().__init__()
        self.id_pago = id_pago
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.id_conversion = id_conversion
        self.monto_comision = monto_comision
        self.moneda = moneda
        self.id_transaccion_externa = id_transaccion_externa
        self.timestamp = timestamp

@dataclass
class ComisionRevertida(EventoDominio):
    """Evento disparado cuando una comisión se revierte"""
    id_pago: str
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto_comision: float
    moneda: str
    motivo_reversion: str
    timestamp: datetime
    
    def __init__(self, id_pago: str, id_embajador: str, id_partner: str, 
                 id_conversion: str, monto_comision: float, moneda: str, 
                 motivo_reversion: str, timestamp: datetime):
        super().__init__()
        self.id_pago = id_pago
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.id_conversion = id_conversion
        self.monto_comision = monto_comision
        self.moneda = moneda
        self.motivo_reversion = motivo_reversion
        self.timestamp = timestamp

@dataclass
class PagoSolicitado(EventoDominio):
    """Evento disparado cuando se solicita un pago desde el servicio de lealtad"""
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto: float
    moneda: str
    informacion_pago: Dict
    detalle_comision: Dict
    timestamp: datetime
    
    def __init__(self, id_embajador: str, id_partner: str, id_conversion: str,
                 monto: float, moneda: str, informacion_pago: Dict, 
                 detalle_comision: Dict, timestamp: datetime):
        super().__init__()
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.id_conversion = id_conversion
        self.monto = monto
        self.moneda = moneda
        self.informacion_pago = informacion_pago
        self.detalle_comision = detalle_comision
        self.timestamp = timestamp
