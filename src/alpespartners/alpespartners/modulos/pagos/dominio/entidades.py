from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from enum import Enum

from .objetos_valor import EstadoPago, TipoPago, InformacionPago, DetalleComision
from .eventos import PagoIniciado, PagoProcesado, PagoFallido, ComisionPagada, ComisionRevertida

@dataclass
class Entidad:
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class AgregacionRaiz(Entidad):
    eventos: List = field(default_factory=list)
    version: int = field(default=0)

    def agregar_evento(self, evento):
        self.eventos.append(evento)
        self.version += 1

class Pago(Entidad):
    """Agregado raíz para manejar pagos de comisiones"""
    
    def __init__(self, 
                 id_embajador: str,
                 id_partner: str,
                 id_conversion: str,
                 monto: float,
                 moneda: str = "USD",
                 estado: EstadoPago = EstadoPago.PENDIENTE,
                 tipo_pago: TipoPago = TipoPago.COMISION,
                 informacion_pago: Optional[InformacionPago] = None,
                 detalle_comision: Optional[DetalleComision] = None,
                 fecha_creacion: Optional[datetime] = None,
                 fecha_procesamiento: Optional[datetime] = None,
                 fecha_finalizacion: Optional[datetime] = None,
                 motivo_fallo: Optional[str] = None,
                 id_transaccion_externa: Optional[str] = None,
                 metadata: Optional[dict] = None,
                 id: Optional[str] = None):
        
        # Llamar al constructor de la clase padre
        super().__init__(id=id)
        
        # Campos requeridos
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.id_conversion = id_conversion
        self.monto = monto
        
        # Campos opcionales
        self.moneda = moneda
        self.estado = estado
        self.tipo_pago = tipo_pago
        self.informacion_pago = informacion_pago
        self.detalle_comision = detalle_comision
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.fecha_procesamiento = fecha_procesamiento
        self.fecha_finalizacion = fecha_finalizacion
        self.motivo_fallo = motivo_fallo
        self.id_transaccion_externa = id_transaccion_externa
        self.metadata = metadata or {}
        
        # Campos para Event Sourcing
        self.eventos: List = []
        self.version: int = 0

    def agregar_evento(self, evento):
        """Agrega un evento a la lista de eventos del agregado"""
        self.eventos.append(evento)
        self.version += 1

    @property
    def id_pago(self) -> str:
        return self.id

    def iniciar_pago(self, informacion_pago: InformacionPago, detalle_comision: DetalleComision):
        """Inicia el proceso de pago"""
        if self.estado != EstadoPago.PENDIENTE:
            raise ValueError(f"No se puede iniciar un pago en estado {self.estado}")
        
        self.informacion_pago = informacion_pago
        self.detalle_comision = detalle_comision
        self.estado = EstadoPago.EN_PROCESO
        
        evento = PagoIniciado(
            id_pago=self.id_pago,
            id_embajador=self.id_embajador,
            id_partner=self.id_partner,
            id_conversion=self.id_conversion,
            monto=self.monto,
            moneda=self.moneda,
            tipo_pago=self.tipo_pago.value,
            informacion_pago=informacion_pago.__dict__,
            detalle_comision=detalle_comision.__dict__,
            timestamp=self.fecha_creacion
        )
        self.agregar_evento(evento)

    def procesar_pago_exitoso(self, id_transaccion_externa: str):
        """Marca el pago como procesado exitosamente"""
        if self.estado != EstadoPago.EN_PROCESO:
            raise ValueError(f"No se puede procesar un pago en estado {self.estado}")
        
        self.estado = EstadoPago.PROCESADO
        self.id_transaccion_externa = id_transaccion_externa
        self.fecha_procesamiento = datetime.now()
        
        evento = PagoProcesado(
            id_pago=self.id_pago,
            id_embajador=self.id_embajador,
            id_partner=self.id_partner,
            id_conversion=self.id_conversion,
            monto=self.monto,
            moneda=self.moneda,
            id_transaccion_externa=id_transaccion_externa,
            timestamp=self.fecha_procesamiento
        )
        self.agregar_evento(evento)

    def procesar_pago_fallido(self, motivo_fallo: str):
        """Marca el pago como fallido"""
        if self.estado not in [EstadoPago.PENDIENTE, EstadoPago.EN_PROCESO]:
            raise ValueError(f"No se puede fallar un pago en estado {self.estado}")
        
        self.estado = EstadoPago.FALLIDO
        self.motivo_fallo = motivo_fallo
        self.fecha_finalizacion = datetime.now()
        
        evento = PagoFallido(
            id_pago=self.id_pago,
            id_embajador=self.id_embajador,
            id_partner=self.id_partner,
            id_conversion=self.id_conversion,
            monto=self.monto,
            moneda=self.moneda,
            motivo_fallo=motivo_fallo,
            timestamp=self.fecha_finalizacion
        )
        self.agregar_evento(evento)

    def registrar_comision_pagada(self):
        """Registra que la comisión fue pagada exitosamente"""
        if self.estado != EstadoPago.PROCESADO:
            raise ValueError(f"No se puede registrar comisión pagada en estado {self.estado}")
        
        evento = ComisionPagada(
            id_pago=self.id_pago,
            id_embajador=self.id_embajador,
            id_partner=self.id_partner,
            id_conversion=self.id_conversion,
            monto_comision=self.monto,
            moneda=self.moneda,
            id_transaccion_externa=self.id_transaccion_externa,
            timestamp=datetime.now()
        )
        self.agregar_evento(evento)

    def revertir_comision(self, motivo_reversion: str):
        """Revierte una comisión ya pagada"""
        if self.estado != EstadoPago.PROCESADO:
            raise ValueError(f"No se puede revertir una comisión en estado {self.estado}")
        
        self.estado = EstadoPago.REVERTIDO
        self.motivo_fallo = motivo_reversion
        self.fecha_finalizacion = datetime.now()
        
        evento = ComisionRevertida(
            id_pago=self.id_pago,
            id_embajador=self.id_embajador,
            id_partner=self.id_partner,
            id_conversion=self.id_conversion,
            monto_comision=self.monto,
            moneda=self.moneda,
            motivo_reversion=motivo_reversion,
            timestamp=self.fecha_finalizacion
        )
        self.agregar_evento(evento)

class EventoPago(Entidad):
    """Evento de dominio para Event Sourcing"""
    
    def __init__(self, 
                 id_pago: str,
                 tipo_evento: str,
                 datos_evento: dict,
                 timestamp: Optional[datetime] = None,
                 version_evento: int = 1,
                 id: Optional[str] = None):
        
        # Llamar al constructor de la clase padre
        super().__init__(id=id)
        
        # Campos requeridos
        self.id_pago = id_pago
        self.tipo_evento = tipo_evento
        self.datos_evento = datos_evento
        
        # Campos opcionales
        self.timestamp = timestamp or datetime.now()
        self.version_evento = version_evento
        
        # Campos para Event Sourcing
        self.eventos: List = []
        self.version: int = 0

    def agregar_evento(self, evento):
        """Agrega un evento a la lista de eventos del agregado"""
        self.eventos.append(evento)
        self.version += 1

    @property
    def id_evento(self) -> str:
        return self.id
