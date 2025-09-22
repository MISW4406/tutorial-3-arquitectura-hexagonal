from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..dominio.entidades import Pago
from ..dominio.repositorios import RepositorioPagos, RepositorioEventosPago, RepositorioOutbox
from ..dominio.servicios import ServicioProcesamientoPagos, ServicioValidacionPagos, ServicioNotificaciones
from ..dominio.objetos_valor import EstadoPago, TipoPago, MetodoPago, InformacionPago, DetalleComision
from ..dominio.eventos import PagoIniciado, PagoProcesado, PagoFallido, ComisionPagada, ComisionRevertida
from .comandos import ComandoCrearPago, ComandoProcesarPago, ComandoRevertirPago, ComandoMarcarPagoFallido
from .queries import QueryObtenerPago, QueryObtenerPagosEmbajador, QueryObtenerPagosPartner, QueryObtenerPagosPendientes, QueryObtenerEstadisticasPagos
from .dto import PagoDTO, InformacionPagoDTO, DetalleComisionDTO, ResultadoPagoDTO, EstadisticasPagosDTO
from ....seedwork.dominio.eventos import Despachador

@dataclass
class ServicioPagos:
    """Servicio de aplicación para manejo de pagos"""
    
    repositorio_pagos: RepositorioPagos
    repositorio_eventos: RepositorioEventosPago
    repositorio_outbox: RepositorioOutbox
    servicio_procesamiento: ServicioProcesamientoPagos
    servicio_validacion: ServicioValidacionPagos
    servicio_notificaciones: ServicioNotificaciones
    despachador: Despachador

    def crear_pago(self, comando: ComandoCrearPago) -> str:
        """Crea un nuevo pago de comisión"""
        
        # Validar información de pago
        informacion_pago = InformacionPago(
            metodo_pago=MetodoPago(comando.metodo_pago),
            datos_beneficiario=comando.datos_beneficiario,
            referencia=comando.referencia,
            descripcion=comando.descripcion,
            metadata=comando.metadata
        )
        
        if not self.servicio_validacion.validar_informacion_pago(informacion_pago):
            raise ValueError("Información de pago inválida")
        
        if not self.servicio_validacion.validar_monto_pago(comando.monto, comando.moneda):
            raise ValueError("Monto de pago inválido")
        
        if not self.servicio_validacion.validar_limites_embajador(comando.id_embajador, comando.monto):
            raise ValueError("El embajador excede los límites de pago")
        
        # Crear agregado de pago
        pago = Pago(
            id_embajador=comando.id_embajador,
            id_partner=comando.id_partner,
            id_conversion=comando.id_conversion,
            monto=comando.monto,
            moneda=comando.moneda,
            tipo_pago=TipoPago.COMISION,
            metadata=comando.metadata
        )
        
        # Crear detalle de comisión
        detalle_comision = DetalleComision(
            id_conversion=comando.id_conversion,
            id_click=None,  # Se puede obtener del tracking
            id_campana="",  # Se puede obtener del tracking
            valor_conversion=comando.monto,
            porcentaje_comision=5.0,  # Configurable
            monto_comision=comando.monto,
            modelo_atribucion="last_click",
            fecha_conversion=comando.timestamp
        )
        
        # Iniciar el pago
        pago.iniciar_pago(informacion_pago, detalle_comision)
        
        # Guardar en repositorio
        self.repositorio_pagos.agregar(pago)
        
        # Guardar eventos (Event Sourcing)
        for evento in pago.eventos:
            evento_pago = self._crear_evento_pago(pago.id_pago, evento)
            self.repositorio_eventos.guardar_evento(evento_pago)
            
            # Publicar evento directamente a Pulsar
            self.despachador.publicar_evento(evento)
            
            # Agregar al outbox para publicación (como respaldo)
            self.repositorio_outbox.agregar_evento_outbox(
                evento_id=str(uuid4()),
                evento_tipo=evento.__class__.__name__,
                evento_datos=self._serializar_datos_evento(evento.__dict__),
                timestamp=evento.timestamp.isoformat()
            )
        
        return pago.id_pago

    def procesar_pago(self, comando: ComandoProcesarPago) -> ResultadoPagoDTO:
        """Procesa un pago existente"""
        
        pago = self.repositorio_pagos.obtener_por_id(comando.id_pago)
        if not pago:
            raise ValueError(f"No se encontró pago con ID {comando.id_pago}")
        
        if pago.estado != EstadoPago.EN_PROCESO:
            raise ValueError(f"El pago debe estar en estado EN_PROCESO para ser procesado")
        
        # Procesar pago con el servicio externo
        resultado = self.servicio_procesamiento.procesar_pago(
            pago.informacion_pago, 
            pago.detalle_comision
        )
        
        if resultado.exitoso:
            pago.procesar_pago_exitoso(resultado.id_transaccion_externa)
            pago.registrar_comision_pagada()
            
            # Notificar al embajador
            self.servicio_notificaciones.notificar_pago_exitoso(
                pago.id_embajador, pago.monto, pago.moneda
            )
        else:
            pago.procesar_pago_fallido(resultado.mensaje)
            
            # Notificar al embajador
            self.servicio_notificaciones.notificar_pago_fallido(
                pago.id_embajador, pago.monto, pago.moneda, resultado.mensaje
            )
        
        # Actualizar repositorio
        self.repositorio_pagos.actualizar(pago)
        
        # Guardar eventos
        for evento in pago.eventos:
            evento_pago = self._crear_evento_pago(pago.id_pago, evento)
            self.repositorio_eventos.guardar_evento(evento_pago)
            
            # Publicar evento directamente a Pulsar
            self.despachador.publicar_evento(evento)
            
            # Agregar al outbox (como respaldo)
            self.repositorio_outbox.agregar_evento_outbox(
                evento_id=str(uuid4()),
                evento_tipo=evento.__class__.__name__,
                evento_datos=self._serializar_datos_evento(evento.__dict__),
                timestamp=evento.timestamp.isoformat()
            )
        
        return ResultadoPagoDTO(
            exitoso=resultado.exitoso,
            id_transaccion_externa=resultado.id_transaccion_externa,
            mensaje=resultado.mensaje,
            codigo_error=resultado.codigo_error,
            timestamp=resultado.timestamp
        )

    def revertir_pago(self, comando: ComandoRevertirPago) -> ResultadoPagoDTO:
        """Revierte un pago procesado"""
        
        pago = self.repositorio_pagos.obtener_por_id(comando.id_pago)
        if not pago:
            raise ValueError(f"No se encontró pago con ID {comando.id_pago}")
        
        if pago.estado != EstadoPago.PROCESADO:
            raise ValueError(f"El pago debe estar PROCESADO para ser revertido")
        
        # Revertir en el servicio externo
        resultado = self.servicio_procesamiento.revertir_pago(
            pago.id_transaccion_externa, comando.motivo_reversion
        )
        
        if resultado.exitoso:
            pago.revertir_comision(comando.motivo_reversion)
            
            # Notificar al embajador
            self.servicio_notificaciones.notificar_comision_revertida(
                pago.id_embajador, pago.monto, pago.moneda, comando.motivo_reversion
            )
        else:
            raise ValueError(f"Error al revertir pago: {resultado.mensaje}")
        
        # Actualizar repositorio
        self.repositorio_pagos.actualizar(pago)
        
        # Guardar eventos
        for evento in pago.eventos:
            evento_pago = self._crear_evento_pago(pago.id_pago, evento)
            self.repositorio_eventos.guardar_evento(evento_pago)
            
            # Publicar evento directamente a Pulsar
            self.despachador.publicar_evento(evento)
            
            # Agregar al outbox (como respaldo)
            self.repositorio_outbox.agregar_evento_outbox(
                evento_id=str(uuid4()),
                evento_tipo=evento.__class__.__name__,
                evento_datos=self._serializar_datos_evento(evento.__dict__),
                timestamp=evento.timestamp.isoformat()
            )
        
        return ResultadoPagoDTO(
            exitoso=resultado.exitoso,
            id_transaccion_externa=resultado.id_transaccion_externa,
            mensaje=resultado.mensaje,
            codigo_error=resultado.codigo_error,
            timestamp=resultado.timestamp
        )

    def obtener_pago(self, query: QueryObtenerPago) -> Optional[PagoDTO]:
        """Obtiene un pago por ID"""
        pago = self.repositorio_pagos.obtener_por_id(query.id_pago)
        if not pago:
            return None
        
        return self._mapear_pago_a_dto(pago)

    def obtener_pagos_embajador(self, query: QueryObtenerPagosEmbajador) -> List[PagoDTO]:
        """Obtiene pagos de un embajador"""
        pagos = self.repositorio_pagos.obtener_por_embajador(query.id_embajador)
        return [self._mapear_pago_a_dto(pago) for pago in pagos]

    def obtener_pagos_partner(self, query: QueryObtenerPagosPartner) -> List[PagoDTO]:
        """Obtiene pagos de un partner"""
        pagos = self.repositorio_pagos.obtener_por_partner(query.id_partner)
        return [self._mapear_pago_a_dto(pago) for pago in pagos]

    def obtener_pagos_pendientes(self, query: QueryObtenerPagosPendientes) -> List[PagoDTO]:
        """Obtiene pagos pendientes de procesamiento"""
        pagos = self.repositorio_pagos.obtener_pendientes()
        return [self._mapear_pago_a_dto(pago) for pago in pagos]

    def obtener_estadisticas(self, query: QueryObtenerEstadisticasPagos) -> EstadisticasPagosDTO:
        """Obtiene estadísticas de pagos"""
        # Obtener todos los pagos para calcular estadísticas
        if query.id_embajador:
            pagos = self.repositorio_pagos.obtener_por_embajador(query.id_embajador)
        elif query.id_partner:
            pagos = self.repositorio_pagos.obtener_por_partner(query.id_partner)
        else:
            # Obtener todos los pagos (implementación simplificada)
            pagos = []
            # En una implementación real, se tendría un método para obtener todos los pagos
        
        # Filtrar por fechas si se especifican
        if query.fecha_desde:
            pagos = [p for p in pagos if p.fecha_creacion >= query.fecha_desde]
        if query.fecha_hasta:
            pagos = [p for p in pagos if p.fecha_creacion <= query.fecha_hasta]
        
        # Calcular estadísticas
        total_pagos = len(pagos)
        total_monto = sum(p.monto for p in pagos)
        pagos_exitosos = len([p for p in pagos if p.estado == EstadoPago.PROCESADO])
        pagos_fallidos = len([p for p in pagos if p.estado == EstadoPago.FALLIDO])
        pagos_pendientes = len([p for p in pagos if p.estado == EstadoPago.PENDIENTE])
        monto_promedio = total_monto / total_pagos if total_pagos > 0 else 0.0
        
        fecha_desde = query.fecha_desde or (min(p.fecha_creacion for p in pagos) if pagos else datetime.now())
        fecha_hasta = query.fecha_hasta or (max(p.fecha_creacion for p in pagos) if pagos else datetime.now())
        
        # Calcular tasa de éxito
        tasa_exito = (pagos_exitosos / total_pagos * 100) if total_pagos > 0 else 0.0
        
        # Contar pagos por estado
        pagos_por_estado = {}
        for pago in pagos:
            estado = pago.estado.value
            pagos_por_estado[estado] = pagos_por_estado.get(estado, 0) + 1
        
        # Contar pagos por tipo
        pagos_por_tipo = {}
        for pago in pagos:
            tipo = pago.tipo_pago.value
            pagos_por_tipo[tipo] = pagos_por_tipo.get(tipo, 0) + 1
        
        # Contar pagos por método
        pagos_por_metodo = {}
        for pago in pagos:
            metodo = pago.informacion_pago.metodo_pago.value if pago.informacion_pago else "DESCONOCIDO"
            pagos_por_metodo[metodo] = pagos_por_metodo.get(metodo, 0) + 1
        
        return EstadisticasPagosDTO(
            total_pagos=total_pagos,
            total_monto=total_monto,
            pagos_exitosos=pagos_exitosos,
            pagos_fallidos=pagos_fallidos,
            pagos_pendientes=pagos_pendientes,
            monto_promedio=monto_promedio,
            tasa_exito=tasa_exito,
            pagos_por_estado=pagos_por_estado,
            pagos_por_tipo=pagos_por_tipo,
            pagos_por_metodo=pagos_por_metodo,
            periodo_desde=fecha_desde,
            periodo_hasta=fecha_hasta
        )

    def _crear_evento_pago(self, id_pago: str, evento_dominio) -> 'EventoPago':
        """Crea un evento de pago para Event Sourcing"""
        from ..dominio.entidades import EventoPago
        
        return EventoPago(
            id_pago=id_pago,
            tipo_evento=evento_dominio.__class__.__name__,
            datos_evento=self._serializar_datos_evento(evento_dominio.__dict__)
        )
    
    def _serializar_datos_evento(self, datos: dict) -> dict:
        """Serializa los datos del evento para almacenamiento JSON"""
        from datetime import datetime
        from enum import Enum
        
        def convertir_objetos(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, dict):
                return {k: convertir_objetos(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convertir_objetos(item) for item in obj]
            else:
                return obj
        
        return convertir_objetos(datos)

    def _mapear_pago_a_dto(self, pago: Pago) -> PagoDTO:
        """Mapea un agregado de pago a DTO"""
        return PagoDTO(
            id_pago=pago.id_pago,
            id_embajador=pago.id_embajador,
            id_partner=pago.id_partner,
            id_conversion=pago.id_conversion,
            monto=pago.monto,
            moneda=pago.moneda,
            estado=pago.estado,
            tipo_pago=pago.tipo_pago,
            metodo_pago=pago.informacion_pago.metodo_pago if pago.informacion_pago else MetodoPago.TRANSFERENCIA_BANCARIA,
            fecha_creacion=pago.fecha_creacion,
            fecha_procesamiento=pago.fecha_procesamiento,
            fecha_finalizacion=pago.fecha_finalizacion,
            motivo_fallo=pago.motivo_fallo,
            id_transaccion_externa=pago.id_transaccion_externa,
            metadata=pago.metadata
        )
