from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..dominio.entidades import Pago, EventoPago
from ..dominio.repositorios import RepositorioPagos, RepositorioEventosPago, RepositorioOutbox
from ..dominio.objetos_valor import EstadoPago, TipoPago, MetodoPago, InformacionPago, DetalleComision
from .modelos import PagoModel, EventoPagoModel, OutboxModel

class RepositorioPagosSQL(RepositorioPagos):
    """Implementación SQL del repositorio de pagos"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def agregar(self, pago: Pago) -> None:
        """Agrega un nuevo pago"""
        modelo = self._mapear_entidad_a_modelo(pago)
        self.session.add(modelo)
        self.session.commit()
        
        # Actualizar el ID de la entidad después del commit
        pago.id = str(modelo.id)
    
    def actualizar(self, pago: Pago) -> None:
        """Actualiza un pago existente"""
        modelo = self.session.query(PagoModel).filter(PagoModel.id == pago.id).first()
        if modelo:
            self._actualizar_modelo_desde_entidad(modelo, pago)
            self.session.commit()
    
    def obtener_por_id(self, id_pago: str) -> Optional[Pago]:
        """Obtiene un pago por su ID"""
        modelo = self.session.query(PagoModel).filter(PagoModel.id == id_pago).first()
        if modelo:
            return self._mapear_modelo_a_entidad(modelo)
        return None
    
    def obtener_por_embajador(self, id_embajador: str) -> List[Pago]:
        """Obtiene todos los pagos de un embajador"""
        modelos = self.session.query(PagoModel).filter(
            PagoModel.id_embajador == id_embajador
        ).order_by(desc(PagoModel.fecha_creacion)).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def obtener_por_partner(self, id_partner: str) -> List[Pago]:
        """Obtiene todos los pagos de un partner"""
        modelos = self.session.query(PagoModel).filter(
            PagoModel.id_partner == id_partner
        ).order_by(desc(PagoModel.fecha_creacion)).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def obtener_por_conversion(self, id_conversion: str) -> List[Pago]:
        """Obtiene todos los pagos de una conversión"""
        modelos = self.session.query(PagoModel).filter(
            PagoModel.id_conversion == id_conversion
        ).order_by(desc(PagoModel.fecha_creacion)).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def obtener_pendientes(self) -> List[Pago]:
        """Obtiene todos los pagos pendientes"""
        modelos = self.session.query(PagoModel).filter(
            PagoModel.estado == EstadoPago.PENDIENTE.value
        ).order_by(PagoModel.fecha_creacion).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def _mapear_entidad_a_modelo(self, pago: Pago) -> PagoModel:
        """Mapea una entidad de pago a modelo SQLAlchemy"""
        return PagoModel(
            id=pago.id,
            id_embajador=pago.id_embajador,
            id_partner=pago.id_partner,
            id_conversion=pago.id_conversion,
            monto=pago.monto,
            moneda=pago.moneda,
            estado=pago.estado.value,
            tipo_pago=pago.tipo_pago.value,
            metodo_pago=pago.informacion_pago.metodo_pago.value if pago.informacion_pago else None,
            fecha_creacion=pago.fecha_creacion,
            fecha_procesamiento=pago.fecha_procesamiento,
            fecha_finalizacion=pago.fecha_finalizacion,
            motivo_fallo=pago.motivo_fallo,
            id_transaccion_externa=pago.id_transaccion_externa,
            metadatos=pago.metadata,
            version=pago.version
        )
    
    def _actualizar_modelo_desde_entidad(self, modelo: PagoModel, pago: Pago) -> None:
        """Actualiza un modelo SQLAlchemy desde una entidad"""
        modelo.estado = pago.estado.value
        modelo.fecha_procesamiento = pago.fecha_procesamiento
        modelo.fecha_finalizacion = pago.fecha_finalizacion
        modelo.motivo_fallo = pago.motivo_fallo
        modelo.id_transaccion_externa = pago.id_transaccion_externa
        modelo.metadatos = pago.metadata
        modelo.version = pago.version
    
    def _mapear_modelo_a_entidad(self, modelo: PagoModel) -> Pago:
        """Mapea un modelo SQLAlchemy a entidad de pago"""
        # Reconstruir información de pago si existe
        informacion_pago = None
        if modelo.metodo_pago:
            informacion_pago = InformacionPago(
                metodo_pago=MetodoPago(modelo.metodo_pago),
                datos_beneficiario={},  # Se debería reconstruir desde metadata
                referencia="",
                descripcion=""
            )
        
        pago = Pago(
            id=str(modelo.id),
            id_embajador=modelo.id_embajador,
            id_partner=modelo.id_partner,
            id_conversion=modelo.id_conversion,
            monto=modelo.monto,
            moneda=modelo.moneda,
            estado=EstadoPago(modelo.estado),
            tipo_pago=TipoPago(modelo.tipo_pago),
            informacion_pago=informacion_pago,
            fecha_creacion=modelo.fecha_creacion,
            fecha_procesamiento=modelo.fecha_procesamiento,
            fecha_finalizacion=modelo.fecha_finalizacion,
            motivo_fallo=modelo.motivo_fallo,
            id_transaccion_externa=modelo.id_transaccion_externa,
            metadata=modelo.metadatos or {}
        )
        
        # Establecer la versión después de crear el objeto
        pago.version = modelo.version
        
        return pago

class RepositorioEventosPagoSQL(RepositorioEventosPago):
    """Implementación SQL del repositorio de eventos de pago"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def guardar_evento(self, evento: EventoPago) -> None:
        """Guarda un evento de pago"""
        modelo = EventoPagoModel(
            id=evento.id,
            id_pago=evento.id_pago,
            tipo_evento=evento.tipo_evento,
            datos_evento=evento.datos_evento,
            timestamp=evento.timestamp,
            version_evento=evento.version_evento
        )
        self.session.add(modelo)
        self.session.commit()
    
    def obtener_eventos_pago(self, id_pago: str) -> List[EventoPago]:
        """Obtiene todos los eventos de un pago específico"""
        modelos = self.session.query(EventoPagoModel).filter(
            EventoPagoModel.id_pago == id_pago
        ).order_by(EventoPagoModel.timestamp).all()
        
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def obtener_eventos_por_tipo(self, tipo_evento: str) -> List[EventoPago]:
        """Obtiene todos los eventos de un tipo específico"""
        modelos = self.session.query(EventoPagoModel).filter(
            EventoPagoModel.tipo_evento == tipo_evento
        ).order_by(EventoPagoModel.timestamp).all()
        
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def obtener_eventos_desde(self, timestamp_desde: str) -> List[EventoPago]:
        """Obtiene eventos desde una fecha específica"""
        fecha_desde = datetime.fromisoformat(timestamp_desde)
        modelos = self.session.query(EventoPagoModel).filter(
            EventoPagoModel.timestamp >= fecha_desde
        ).order_by(EventoPagoModel.timestamp).all()
        
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def _mapear_modelo_a_entidad(self, modelo: EventoPagoModel) -> EventoPago:
        """Mapea un modelo SQLAlchemy a entidad de evento"""
        return EventoPago(
            id=str(modelo.id),
            id_pago=str(modelo.id_pago),
            tipo_evento=modelo.tipo_evento,
            datos_evento=modelo.datos_evento,
            timestamp=modelo.timestamp,
            version_evento=modelo.version_evento
        )

class RepositorioOutboxSQL(RepositorioOutbox):
    """Implementación SQL del repositorio Outbox"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def agregar_evento_outbox(self, evento_id: str, evento_tipo: str, 
                            evento_datos: dict, timestamp: str) -> None:
        """Agrega un evento al outbox"""
        modelo = OutboxModel(
            evento_id=evento_id,
            evento_tipo=evento_tipo,
            evento_datos=evento_datos,
            timestamp=datetime.fromisoformat(timestamp)
        )
        self.session.add(modelo)
        self.session.commit()
    
    def obtener_eventos_pendientes(self) -> List[dict]:
        """Obtiene eventos pendientes de publicación"""
        modelos = self.session.query(OutboxModel).filter(
            OutboxModel.publicado == False
        ).order_by(OutboxModel.timestamp).all()
        
        return [{
            'id': str(modelo.id),
            'evento_id': modelo.evento_id,
            'evento_tipo': modelo.evento_tipo,
            'evento_datos': modelo.evento_datos,
            'timestamp': modelo.timestamp.isoformat(),
            'reintentos': modelo.reintentos
        } for modelo in modelos]
    
    def marcar_evento_publicado(self, evento_id: str) -> None:
        """Marca un evento como publicado"""
        modelo = self.session.query(OutboxModel).filter(
            OutboxModel.evento_id == evento_id
        ).first()
        
        if modelo:
            modelo.publicado = True
            modelo.fecha_publicacion = datetime.now()
            self.session.commit()
    
    def limpiar_eventos_antiguos(self, dias_antiguedad: int) -> None:
        """Limpia eventos antiguos ya publicados"""
        fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)
        
        self.session.query(OutboxModel).filter(
            and_(
                OutboxModel.publicado == True,
                OutboxModel.fecha_publicacion < fecha_limite
            )
        ).delete()
        
        self.session.commit()
