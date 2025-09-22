from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ..modulos.afiliados.aplicacion.comandos import (
    ComandoCrearAfiliado,
    ComandoActualizarAfiliado,
    ComandoActivarAfiliado,
    ComandoDesactivarAfiliado,
    ComandoSuspenderAfiliado,
    ComandoEliminarAfiliado
)
from ..modulos.afiliados.aplicacion.queries import (
    QueryObtenerAfiliado,
    QueryObtenerAfiliadoPorCodigo,
    QueryObtenerAfiliadoPorEmail,
    QueryBuscarAfiliados,
    QueryListarAfiliados,
    QueryObtenerAfiliadosPorEstado,
    QueryObtenerAfiliadosPorTipo,
    QueryContarAfiliados
)
from ..modulos.afiliados.aplicacion.dto import (
    AfiliadoDTO,
    InformacionContactoDTO,
    InformacionFiscalDTO,
    ConfiguracionAfiliadoDTO,
    ResultadoAfiliadoDTO,
    EstadisticasAfiliadosDTO
)
from ..modulos.afiliados.dominio.objetos_valor import EstadoAfiliado, TipoAfiliado
from ..modulos.afiliados.aplicacion.servicios import ServicioAfiliados

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

# Dependencia para obtener el servicio de afiliados
def get_servicio_afiliados():
    """Dependencia para obtener el servicio de afiliados configurado"""
    from ..modulos.afiliados.infraestructura.repositorios import RepositorioAfiliadosSQL
    from ..modulos.afiliados.infraestructura.despachadores import DespachadorEventosAfiliados
    from ..config.database import get_db_session
    from ..config.pulsar import get_pulsar_client, TOPICS
    
    # Obtener sesión de base de datos
    session = next(get_db_session())
    
    # Configurar repositorio
    repositorio_afiliados = RepositorioAfiliadosSQL(session)
    
    # Configurar despachador de eventos
    pulsar_client = get_pulsar_client()
    despachador_eventos = DespachadorEventosAfiliados(
        pulsar_client=pulsar_client,
        topic_afiliados=TOPICS["AFILIADOS_EVENTOS"]
    )
    
    # Crear servicio de aplicación
    return ServicioAfiliados(
        repositorio_afiliados=repositorio_afiliados,
        despachador_eventos=despachador_eventos
    )

# Modelos Pydantic para requests
class CrearAfiliadoRequest(BaseModel):
    codigo_afiliado: str = Field(..., description="Código único del afiliado")
    nombre: str = Field(..., description="Nombre del afiliado")
    tipo_afiliado: str = Field(..., description="Tipo de afiliado")
    email: str = Field(..., description="Email del afiliado")
    telefono: Optional[str] = Field(None, description="Teléfono del afiliado")
    direccion: Optional[str] = Field(None, description="Dirección del afiliado")
    ciudad: Optional[str] = Field(None, description="Ciudad del afiliado")
    pais: Optional[str] = Field(None, description="País del afiliado")
    codigo_postal: Optional[str] = Field(None, description="Código postal")
    tipo_documento: str = Field(default="DNI", description="Tipo de documento")
    numero_documento: str = Field(..., description="Número de documento")
    nombre_fiscal: str = Field(..., description="Nombre fiscal")
    direccion_fiscal: Optional[str] = Field(None, description="Dirección fiscal")
    comision_porcentaje: float = Field(default=5.0, description="Porcentaje de comisión")
    limite_mensual: Optional[float] = Field(None, description="Límite mensual")
    metodo_pago_preferido: str = Field(default="TRANSFERENCIA_BANCARIA", description="Método de pago preferido")
    notificaciones_email: bool = Field(default=True, description="Notificaciones por email")
    notificaciones_sms: bool = Field(default=False, description="Notificaciones por SMS")
    notas: Optional[str] = Field(None, description="Notas adicionales")
    metadata: Optional[dict] = Field(None, description="Metadata adicional")

class ActualizarAfiliadoRequest(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre del afiliado")
    email: Optional[str] = Field(None, description="Email del afiliado")
    telefono: Optional[str] = Field(None, description="Teléfono del afiliado")
    direccion: Optional[str] = Field(None, description="Dirección del afiliado")
    ciudad: Optional[str] = Field(None, description="Ciudad del afiliado")
    pais: Optional[str] = Field(None, description="País del afiliado")
    codigo_postal: Optional[str] = Field(None, description="Código postal")
    comision_porcentaje: Optional[float] = Field(None, description="Porcentaje de comisión")
    limite_mensual: Optional[float] = Field(None, description="Límite mensual")
    metodo_pago_preferido: Optional[str] = Field(None, description="Método de pago preferido")
    notificaciones_email: Optional[bool] = Field(None, description="Notificaciones por email")
    notificaciones_sms: Optional[bool] = Field(None, description="Notificaciones por SMS")
    notas: Optional[str] = Field(None, description="Notas adicionales")
    metadata: Optional[dict] = Field(None, description="Metadata adicional")

class ActivarAfiliadoRequest(BaseModel):
    notas: Optional[str] = Field(None, description="Notas sobre la activación")

class DesactivarAfiliadoRequest(BaseModel):
    motivo: str = Field(..., description="Motivo de la desactivación")

class SuspenderAfiliadoRequest(BaseModel):
    motivo: str = Field(..., description="Motivo de la suspensión")

# Modelos Pydantic para responses
class AfiliadoResponse(BaseModel):
    id_afiliado: str
    codigo_afiliado: str
    nombre: str
    tipo_afiliado: str
    estado: str
    informacion_contacto: InformacionContactoDTO
    informacion_fiscal: InformacionFiscalDTO
    configuracion: ConfiguracionAfiliadoDTO
    fecha_registro: datetime
    fecha_ultima_actividad: Optional[datetime] = None
    notas: Optional[str] = None
    metadata: dict

class ResultadoAfiliadoResponse(BaseModel):
    exitoso: bool
    mensaje: str
    id_afiliado: Optional[str] = None
    codigo_error: Optional[str] = None

class EstadisticasAfiliadosResponse(BaseModel):
    total_afiliados: int
    afiliados_activos: int
    afiliados_inactivos: int
    afiliados_suspendidos: int
    afiliados_pendientes: int
    por_tipo: dict
    por_ciudad: dict
    por_pais: dict
    tasa_activacion: float

# Endpoints

@router.post("/afiliados", response_model=AfiliadoResponse, status_code=status.HTTP_201_CREATED)
async def crear_afiliado(
    request: CrearAfiliadoRequest,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Crear un nuevo afiliado"""
    try:
        comando = ComandoCrearAfiliado(
            codigo_afiliado=request.codigo_afiliado,
            nombre=request.nombre,
            tipo_afiliado=request.tipo_afiliado,
            email=request.email,
            telefono=request.telefono,
            direccion=request.direccion,
            ciudad=request.ciudad,
            pais=request.pais,
            codigo_postal=request.codigo_postal,
            tipo_documento=request.tipo_documento,
            numero_documento=request.numero_documento,
            nombre_fiscal=request.nombre_fiscal,
            direccion_fiscal=request.direccion_fiscal,
            comision_porcentaje=request.comision_porcentaje,
            limite_mensual=request.limite_mensual,
            metodo_pago_preferido=request.metodo_pago_preferido,
            notificaciones_email=request.notificaciones_email,
            notificaciones_sms=request.notificaciones_sms,
            notas=request.notas,
            metadata=request.metadata
        )
        
        id_afiliado = servicio.crear_afiliado(comando)
        
        # Obtener el afiliado creado para la respuesta
        query = QueryObtenerAfiliado(id_afiliado=id_afiliado)
        afiliado_dto = servicio.obtener_afiliado(query)
        
        if not afiliado_dto:
            raise HTTPException(status_code=404, detail="Afiliado no encontrado después de crear")
        
        return AfiliadoResponse(
            id_afiliado=afiliado_dto.id_afiliado,
            codigo_afiliado=afiliado_dto.codigo_afiliado,
            nombre=afiliado_dto.nombre,
            tipo_afiliado=afiliado_dto.tipo_afiliado,
            estado=afiliado_dto.estado,
            informacion_contacto=afiliado_dto.informacion_contacto,
            informacion_fiscal=afiliado_dto.informacion_fiscal,
            configuracion=afiliado_dto.configuracion,
            fecha_registro=afiliado_dto.fecha_registro,
            fecha_ultima_actividad=afiliado_dto.fecha_ultima_actividad,
            notas=afiliado_dto.notas,
            metadata=afiliado_dto.metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creando afiliado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/afiliados", response_model=List[AfiliadoResponse])
async def listar_afiliados(
    limite: int = Query(100, description="Límite de resultados"),
    offset: int = Query(0, description="Offset para paginación"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad"),
    pais: Optional[str] = Query(None, description="Filtrar por país"),
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Listar afiliados con filtros opcionales"""
    try:
        if nombre or estado or tipo or ciudad or pais:
            # Búsqueda con filtros
            query = QueryBuscarAfiliados(
                nombre=nombre,
                estado=estado,
                tipo=tipo,
                ciudad=ciudad,
                pais=pais,
                limite=limite,
                offset=offset
            )
            afiliados_dto = servicio.buscar_afiliados(query)
        else:
            # Listado simple
            query = QueryListarAfiliados(limite=limite, offset=offset)
            afiliados_dto = servicio.listar_afiliados(query)
        
        return [
            AfiliadoResponse(
                id_afiliado=afiliado.id_afiliado,
                codigo_afiliado=afiliado.codigo_afiliado,
                nombre=afiliado.nombre,
                tipo_afiliado=afiliado.tipo_afiliado,
                estado=afiliado.estado,
                informacion_contacto=afiliado.informacion_contacto,
                informacion_fiscal=afiliado.informacion_fiscal,
                configuracion=afiliado.configuracion,
                fecha_registro=afiliado.fecha_registro,
                fecha_ultima_actividad=afiliado.fecha_ultima_actividad,
                notas=afiliado.notas,
                metadata=afiliado.metadata
            )
            for afiliado in afiliados_dto
        ]
        
    except Exception as e:
        logger.error(f"Error listando afiliados: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/afiliados/estadisticas", response_model=EstadisticasAfiliadosResponse)
async def obtener_estadisticas(
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Obtener estadísticas de afiliados"""
    try:
        estadisticas = servicio.obtener_estadisticas()
        
        return EstadisticasAfiliadosResponse(
            total_afiliados=estadisticas.total_afiliados,
            afiliados_activos=estadisticas.afiliados_activos,
            afiliados_inactivos=estadisticas.afiliados_inactivos,
            afiliados_suspendidos=estadisticas.afiliados_suspendidos,
            afiliados_pendientes=estadisticas.afiliados_pendientes,
            por_tipo=estadisticas.por_tipo,
            por_ciudad=estadisticas.por_ciudad,
            por_pais=estadisticas.por_pais,
            tasa_activacion=estadisticas.tasa_activacion
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoints de información
@router.get("/afiliados/estados", response_model=List[str])
async def obtener_estados_afiliado():
    """Obtener lista de estados de afiliado disponibles"""
    return [estado.value for estado in EstadoAfiliado]

@router.get("/afiliados/tipos", response_model=List[str])
async def obtener_tipos_afiliado():
    """Obtener lista de tipos de afiliado disponibles"""
    return [tipo.value for tipo in TipoAfiliado]


@router.get("/afiliados/codigo/{codigo_afiliado}", response_model=AfiliadoResponse)
async def obtener_afiliado_por_codigo(
    codigo_afiliado: str,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Obtener un afiliado por código"""
    try:
        query = QueryObtenerAfiliadoPorCodigo(codigo_afiliado=codigo_afiliado)
        afiliado_dto = servicio.obtener_afiliado_por_codigo(query)
        
        if not afiliado_dto:
            raise HTTPException(status_code=404, detail="Afiliado no encontrado")
        
        return AfiliadoResponse(
            id_afiliado=afiliado_dto.id_afiliado,
            codigo_afiliado=afiliado_dto.codigo_afiliado,
            nombre=afiliado_dto.nombre,
            tipo_afiliado=afiliado_dto.tipo_afiliado,
            estado=afiliado_dto.estado,
            informacion_contacto=afiliado_dto.informacion_contacto,
            informacion_fiscal=afiliado_dto.informacion_fiscal,
            configuracion=afiliado_dto.configuracion,
            fecha_registro=afiliado_dto.fecha_registro,
            fecha_ultima_actividad=afiliado_dto.fecha_ultima_actividad,
            notas=afiliado_dto.notas,
            metadata=afiliado_dto.metadata
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo afiliado por código: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/afiliados/{id_afiliado}", response_model=ResultadoAfiliadoResponse)
async def actualizar_afiliado(
    id_afiliado: str,
    request: ActualizarAfiliadoRequest,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Actualizar un afiliado existente"""
    try:
        comando = ComandoActualizarAfiliado(
            id_afiliado=id_afiliado,
            nombre=request.nombre,
            email=request.email,
            telefono=request.telefono,
            direccion=request.direccion,
            ciudad=request.ciudad,
            pais=request.pais,
            codigo_postal=request.codigo_postal,
            comision_porcentaje=request.comision_porcentaje,
            limite_mensual=request.limite_mensual,
            metodo_pago_preferido=request.metodo_pago_preferido,
            notificaciones_email=request.notificaciones_email,
            notificaciones_sms=request.notificaciones_sms,
            notas=request.notas,
            metadata=request.metadata
        )
        
        resultado = servicio.actualizar_afiliado(comando)
        
        return ResultadoAfiliadoResponse(
            exitoso=resultado.exitoso,
            mensaje=resultado.mensaje,
            id_afiliado=resultado.id_afiliado,
            codigo_error=resultado.codigo_error
        )
        
    except Exception as e:
        logger.error(f"Error actualizando afiliado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/afiliados/{id_afiliado}/activar", response_model=ResultadoAfiliadoResponse)
async def activar_afiliado(
    id_afiliado: str,
    request: ActivarAfiliadoRequest,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Activar un afiliado"""
    try:
        comando = ComandoActivarAfiliado(
            id_afiliado=id_afiliado,
            notas=request.notas
        )
        
        resultado = servicio.activar_afiliado(comando)
        
        return ResultadoAfiliadoResponse(
            exitoso=resultado.exitoso,
            mensaje=resultado.mensaje,
            id_afiliado=resultado.id_afiliado,
            codigo_error=resultado.codigo_error
        )
        
    except Exception as e:
        logger.error(f"Error activando afiliado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/afiliados/{id_afiliado}/desactivar", response_model=ResultadoAfiliadoResponse)
async def desactivar_afiliado(
    id_afiliado: str,
    request: DesactivarAfiliadoRequest,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Desactivar un afiliado"""
    try:
        comando = ComandoDesactivarAfiliado(
            id_afiliado=id_afiliado,
            motivo=request.motivo
        )
        
        resultado = servicio.desactivar_afiliado(comando)
        
        return ResultadoAfiliadoResponse(
            exitoso=resultado.exitoso,
            mensaje=resultado.mensaje,
            id_afiliado=resultado.id_afiliado,
            codigo_error=resultado.codigo_error
        )
        
    except Exception as e:
        logger.error(f"Error desactivando afiliado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/afiliados/{id_afiliado}/suspender", response_model=ResultadoAfiliadoResponse)
async def suspender_afiliado(
    id_afiliado: str,
    request: SuspenderAfiliadoRequest,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Suspender un afiliado"""
    try:
        comando = ComandoSuspenderAfiliado(
            id_afiliado=id_afiliado,
            motivo=request.motivo
        )
        
        resultado = servicio.suspender_afiliado(comando)
        
        return ResultadoAfiliadoResponse(
            exitoso=resultado.exitoso,
            mensaje=resultado.mensaje,
            id_afiliado=resultado.id_afiliado,
            codigo_error=resultado.codigo_error
        )
        
    except Exception as e:
        logger.error(f"Error suspendiendo afiliado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/afiliados/{id_afiliado}", response_model=ResultadoAfiliadoResponse)
async def eliminar_afiliado(
    id_afiliado: str,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Eliminar un afiliado"""
    try:
        comando = ComandoEliminarAfiliado(id_afiliado=id_afiliado)
        resultado = servicio.eliminar_afiliado(comando)
        
        return ResultadoAfiliadoResponse(
            exitoso=resultado.exitoso,
            mensaje=resultado.mensaje,
            id_afiliado=resultado.id_afiliado,
            codigo_error=resultado.codigo_error
        )
        
    except Exception as e:
        logger.error(f"Error eliminando afiliado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoints de consulta
@router.get("/afiliados/{id_afiliado}", response_model=AfiliadoResponse)
async def obtener_afiliado(
    id_afiliado: str,
    servicio: ServicioAfiliados = Depends(get_servicio_afiliados)
):
    """Obtener un afiliado por ID"""
    try:
        query = QueryObtenerAfiliado(id_afiliado=id_afiliado)
        afiliado_dto = servicio.obtener_afiliado(query)
        
        if not afiliado_dto:
            raise HTTPException(status_code=404, detail="Afiliado no encontrado")
        
        return AfiliadoResponse(
            id_afiliado=afiliado_dto.id_afiliado,
            codigo_afiliado=afiliado_dto.codigo_afiliado,
            nombre=afiliado_dto.nombre,
            tipo_afiliado=afiliado_dto.tipo_afiliado,
            estado=afiliado_dto.estado,
            informacion_contacto=afiliado_dto.informacion_contacto,
            informacion_fiscal=afiliado_dto.informacion_fiscal,
            configuracion=afiliado_dto.configuracion,
            fecha_registro=afiliado_dto.fecha_registro,
            fecha_ultima_actividad=afiliado_dto.fecha_ultima_actividad,
            notas=afiliado_dto.notas,
            metadata=afiliado_dto.metadata
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo afiliado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")



