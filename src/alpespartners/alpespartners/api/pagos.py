from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ..modulos.pagos.aplicacion.comandos import (
    ComandoCrearPago, 
    ComandoProcesarPago, 
    ComandoRevertirPago,
    ComandoMarcarPagoFallido
)
from ..modulos.pagos.aplicacion.queries import (
    QueryObtenerPago,
    QueryObtenerPagosEmbajador,
    QueryObtenerPagosPartner,
    QueryObtenerPagosPendientes,
    QueryObtenerEstadisticasPagos
)
from ..modulos.pagos.aplicacion.dto import (
    PagoDTO,
    InformacionPagoDTO,
    DetalleComisionDTO,
    ResultadoPagoDTO,
    EstadisticasPagosDTO,
    EstadoPago,
    TipoPago,
    MetodoPago
)
from ..modulos.pagos.aplicacion.servicios import ServicioPagos

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

# Dependencia para obtener el servicio de pagos
def get_servicio_pagos():
    """Dependencia para obtener el servicio de pagos configurado"""
    from ..modulos.pagos.infraestructura.repositorios import (
        RepositorioPagosSQL, 
        RepositorioEventosPagoSQL, 
        RepositorioOutboxSQL
    )
    from ..modulos.pagos.infraestructura.servicios import (
        ServicioProcesamientoPagosSimulado,
        ServicioValidacionPagosImpl,
        ServicioNotificacionesSimulado
    )
    from ..modulos.pagos.infraestructura.despachadores import DespachadorEventosPago
    from ..config.database import get_db_session
    from ..config.pulsar import get_pulsar_client, TOPICS
    
    # Obtener sesión de base de datos
    session = next(get_db_session())
    
    # Obtener cliente Pulsar
    pulsar_client = get_pulsar_client()
    
    # Configurar repositorios
    repositorio_pagos = RepositorioPagosSQL(session)
    repositorio_eventos = RepositorioEventosPagoSQL(session)
    repositorio_outbox = RepositorioOutboxSQL(session)
    
    # Configurar servicios de dominio
    servicio_procesamiento = ServicioProcesamientoPagosSimulado(
        tasa_exito=0.95,
        delay_min=0.5,
        delay_max=2.0
    )
    servicio_validacion = ServicioValidacionPagosImpl()
    servicio_notificaciones = ServicioNotificacionesSimulado()
    
    # Configurar despachador
    despachador = DespachadorEventosPago(pulsar_client, TOPICS["PAGOS_EVENTOS"])
    
    # Crear servicio de aplicación
    return ServicioPagos(
        repositorio_pagos=repositorio_pagos,
        repositorio_eventos=repositorio_eventos,
        repositorio_outbox=repositorio_outbox,
        servicio_procesamiento=servicio_procesamiento,
        servicio_validacion=servicio_validacion,
        servicio_notificaciones=servicio_notificaciones,
        despachador=despachador
    )

# Modelos Pydantic para requests
class CrearPagoRequest(BaseModel):
    id_embajador: str = Field(..., description="ID del embajador")
    id_partner: str = Field(..., description="ID del partner")
    id_conversion: str = Field(..., description="ID de la conversión")
    monto: float = Field(..., gt=0, description="Monto del pago")
    moneda: str = Field(default="USD", description="Moneda del pago")
    metodo_pago: str = Field(..., description="Método de pago")
    datos_beneficiario: dict = Field(..., description="Datos del beneficiario")
    referencia: str = Field(..., description="Referencia del pago")
    descripcion: str = Field(..., description="Descripción del pago")
    metadata: Optional[dict] = Field(default=None, description="Metadata adicional")

class ProcesarPagoRequest(BaseModel):
    id_pago: str = Field(..., description="ID del pago a procesar")

class RevertirPagoRequest(BaseModel):
    id_pago: str = Field(..., description="ID del pago a revertir")
    motivo_reversion: str = Field(..., description="Motivo de la reversión")

class MarcarPagoFallidoRequest(BaseModel):
    id_pago: str = Field(..., description="ID del pago a marcar como fallido")
    motivo_fallo: str = Field(..., description="Motivo del fallo")

# Modelos Pydantic para responses
class PagoResponse(BaseModel):
    id_pago: str
    id_embajador: str
    id_partner: str
    id_conversion: str
    monto: float
    moneda: str
    estado: str
    tipo_pago: str
    metodo_pago: str
    fecha_creacion: datetime
    fecha_procesamiento: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    motivo_fallo: Optional[str] = None
    id_transaccion_externa: Optional[str] = None
    metadata: dict

class ResultadoPagoResponse(BaseModel):
    exitoso: bool
    id_transaccion_externa: Optional[str] = None
    mensaje: str
    codigo_error: Optional[str] = None
    timestamp: datetime

class EstadisticasResponse(BaseModel):
    total_pagos: int
    total_monto: float
    pagos_exitosos: int
    pagos_fallidos: int
    pagos_pendientes: int
    monto_promedio: float
    tasa_exito: float
    pagos_por_estado: dict
    pagos_por_tipo: dict
    pagos_por_metodo: dict

# Endpoints

@router.post("/pagos", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
async def crear_pago(
    request: CrearPagoRequest,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Crear un nuevo pago de comisión"""
    try:
        comando = ComandoCrearPago(
            id_embajador=request.id_embajador,
            id_partner=request.id_partner,
            id_conversion=request.id_conversion,
            monto=request.monto,
            moneda=request.moneda,
            metodo_pago=request.metodo_pago,
            datos_beneficiario=request.datos_beneficiario,
            referencia=request.referencia,
            descripcion=request.descripcion,
            metadata=request.metadata or {}
        )
        
        id_pago = servicio.crear_pago(comando)
        
        # Obtener el pago creado para la respuesta
        query = QueryObtenerPago(id_pago=id_pago)
        pago_dto = servicio.obtener_pago(query)
        
        if not pago_dto:
            raise HTTPException(status_code=404, detail="Pago no encontrado después de crear")
        
        return PagoResponse(
            id_pago=pago_dto.id_pago,
            id_embajador=pago_dto.id_embajador,
            id_partner=pago_dto.id_partner,
            id_conversion=pago_dto.id_conversion,
            monto=pago_dto.monto,
            moneda=pago_dto.moneda,
            estado=pago_dto.estado.value,
            tipo_pago=pago_dto.tipo_pago.value,
            metodo_pago=pago_dto.metodo_pago.value,
            fecha_creacion=pago_dto.fecha_creacion,
            fecha_procesamiento=pago_dto.fecha_procesamiento,
            fecha_finalizacion=pago_dto.fecha_finalizacion,
            motivo_fallo=pago_dto.motivo_fallo,
            id_transaccion_externa=pago_dto.id_transaccion_externa,
            metadata=pago_dto.metadata
        )
        
    except ValueError as e:
        logger.error(f"Error creando pago: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creando pago: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/pagos/{id_pago}/procesar", response_model=ResultadoPagoResponse)
async def procesar_pago(
    id_pago: str,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Procesar un pago existente"""
    try:
        comando = ComandoProcesarPago(id_pago=id_pago)
        resultado = servicio.procesar_pago(comando)
        
        return ResultadoPagoResponse(
            exitoso=resultado.exitoso,
            id_transaccion_externa=resultado.id_transaccion_externa,
            mensaje=resultado.mensaje,
            codigo_error=resultado.codigo_error,
            timestamp=resultado.timestamp
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error procesando pago: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/pagos/{id_pago}/revertir", response_model=ResultadoPagoResponse)
async def revertir_pago(
    id_pago: str,
    request: RevertirPagoRequest,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Revertir un pago procesado"""
    try:
        comando = ComandoRevertirPago(
            id_pago=id_pago,
            motivo_reversion=request.motivo_reversion
        )
        resultado = servicio.revertir_pago(comando)
        
        return ResultadoPagoResponse(
            exitoso=resultado.exitoso,
            id_transaccion_externa=resultado.id_transaccion_externa,
            mensaje=resultado.mensaje,
            codigo_error=resultado.codigo_error,
            timestamp=resultado.timestamp
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error revirtiendo pago: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoints específicos (deben ir antes de los endpoints con parámetros)
@router.get("/pagos/estados", response_model=List[str])
async def obtener_estados_pago():
    """Obtener lista de estados de pago disponibles"""
    return [estado.value for estado in EstadoPago]

@router.get("/pagos/metodos", response_model=List[str])
async def obtener_metodos_pago():
    """Obtener lista de métodos de pago disponibles"""
    return [metodo.value for metodo in MetodoPago]

@router.get("/pagos/tipos", response_model=List[str])
async def obtener_tipos_pago():
    """Obtener lista de tipos de pago disponibles"""
    return [tipo.value for tipo in TipoPago]

@router.get("/pagos/pendientes", response_model=List[PagoResponse])
async def obtener_pagos_pendientes(
    limite: int = 50,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Obtener pagos pendientes"""
    try:
        query = QueryObtenerPagosPendientes(limite=limite)
        pagos_dto = servicio.obtener_pagos_pendientes(query)
        
        return [
            PagoResponse(
                id_pago=pago.id_pago,
                id_embajador=pago.id_embajador,
                id_partner=pago.id_partner,
                id_conversion=pago.id_conversion,
                monto=pago.monto,
                moneda=pago.moneda,
                estado=pago.estado.value,
                tipo_pago=pago.tipo_pago.value,
                metodo_pago=pago.metodo_pago.value,
                fecha_creacion=pago.fecha_creacion,
                fecha_procesamiento=pago.fecha_procesamiento,
                fecha_finalizacion=pago.fecha_finalizacion,
                motivo_fallo=pago.motivo_fallo,
                id_transaccion_externa=pago.id_transaccion_externa,
                metadata=pago.metadata
            )
            for pago in pagos_dto
        ]
        
    except Exception as e:
        logger.error(f"Error obteniendo pagos pendientes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/pagos/estadisticas", response_model=EstadisticasResponse)
async def obtener_estadisticas(
    id_embajador: Optional[str] = None,
    id_partner: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Obtener estadísticas de pagos"""
    try:
        query = QueryObtenerEstadisticasPagos(
            id_embajador=id_embajador,
            id_partner=id_partner,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        estadisticas = servicio.obtener_estadisticas(query)
        
        return EstadisticasResponse(
            total_pagos=estadisticas.total_pagos,
            total_monto=estadisticas.total_monto,
            pagos_exitosos=estadisticas.pagos_exitosos,
            pagos_fallidos=estadisticas.pagos_fallidos,
            pagos_pendientes=estadisticas.pagos_pendientes,
            monto_promedio=estadisticas.monto_promedio,
            tasa_exito=estadisticas.tasa_exito,
            pagos_por_estado=estadisticas.pagos_por_estado,
            pagos_por_tipo=estadisticas.pagos_por_tipo,
            pagos_por_metodo=estadisticas.pagos_por_metodo
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoints con parámetros (deben ir después de los endpoints específicos)
@router.get("/pagos/{id_pago}", response_model=PagoResponse)
async def obtener_pago(
    id_pago: str,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Obtener un pago por ID"""
    try:
        query = QueryObtenerPago(id_pago=id_pago)
        pago_dto = servicio.obtener_pago(query)
        
        if not pago_dto:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        return PagoResponse(
            id_pago=pago_dto.id_pago,
            id_embajador=pago_dto.id_embajador,
            id_partner=pago_dto.id_partner,
            id_conversion=pago_dto.id_conversion,
            monto=pago_dto.monto,
            moneda=pago_dto.moneda,
            estado=pago_dto.estado.value,
            tipo_pago=pago_dto.tipo_pago.value,
            metodo_pago=pago_dto.metodo_pago.value,
            fecha_creacion=pago_dto.fecha_creacion,
            fecha_procesamiento=pago_dto.fecha_procesamiento,
            fecha_finalizacion=pago_dto.fecha_finalizacion,
            motivo_fallo=pago_dto.motivo_fallo,
            id_transaccion_externa=pago_dto.id_transaccion_externa,
            metadata=pago_dto.metadata
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo pago: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/pagos/embajador/{id_embajador}", response_model=List[PagoResponse])
async def obtener_pagos_embajador(
    id_embajador: str,
    estado: Optional[str] = None,
    limite: int = 100,
    offset: int = 0,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Obtener pagos de un embajador"""
    try:
        estado_enum = None
        if estado:
            try:
                estado_enum = EstadoPago(estado)
            except ValueError:
                raise HTTPException(status_code=400, detail="Estado de pago inválido")
        
        query = QueryObtenerPagosEmbajador(
            id_embajador=id_embajador,
            estado=estado_enum,
            limite=limite,
            offset=offset
        )
        pagos = servicio.obtener_pagos_embajador(query)
        
        return [
            PagoResponse(
                id_pago=pago.id_pago,
                id_embajador=pago.id_embajador,
                id_partner=pago.id_partner,
                id_conversion=pago.id_conversion,
                monto=pago.monto,
                moneda=pago.moneda,
                estado=pago.estado.value,
                tipo_pago=pago.tipo_pago.value,
                metodo_pago=pago.metodo_pago.value,
                fecha_creacion=pago.fecha_creacion,
                fecha_procesamiento=pago.fecha_procesamiento,
                fecha_finalizacion=pago.fecha_finalizacion,
                motivo_fallo=pago.motivo_fallo,
                id_transaccion_externa=pago.id_transaccion_externa,
                metadata=pago.metadata
            )
            for pago in pagos
        ]
        
    except Exception as e:
        logger.error(f"Error obteniendo pagos de embajador: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/pagos/partner/{id_partner}", response_model=List[PagoResponse])
async def obtener_pagos_partner(
    id_partner: str,
    estado: Optional[str] = None,
    limite: int = 100,
    offset: int = 0,
    servicio: ServicioPagos = Depends(get_servicio_pagos)
):
    """Obtener pagos de un partner"""
    try:
        estado_enum = None
        if estado:
            try:
                estado_enum = EstadoPago(estado)
            except ValueError:
                raise HTTPException(status_code=400, detail="Estado de pago inválido")
        
        query = QueryObtenerPagosPartner(
            id_partner=id_partner,
            estado=estado_enum,
            limite=limite,
            offset=offset
        )
        pagos = servicio.obtener_pagos_partner(query)
        
        return [
            PagoResponse(
                id_pago=pago.id_pago,
                id_embajador=pago.id_embajador,
                id_partner=pago.id_partner,
                id_conversion=pago.id_conversion,
                monto=pago.monto,
                moneda=pago.moneda,
                estado=pago.estado.value,
                tipo_pago=pago.tipo_pago.value,
                metodo_pago=pago.metodo_pago.value,
                fecha_creacion=pago.fecha_creacion,
                fecha_procesamiento=pago.fecha_procesamiento,
                fecha_finalizacion=pago.fecha_finalizacion,
                motivo_fallo=pago.motivo_fallo,
                id_transaccion_externa=pago.id_transaccion_externa,
                metadata=pago.metadata
            )
            for pago in pagos
        ]
        
    except Exception as e:
        logger.error(f"Error obteniendo pagos de partner: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")