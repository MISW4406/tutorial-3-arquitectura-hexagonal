from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from ..modulos.saga.aplicacion.servicios import ServicioSagaOrquestador
from ..modulos.saga.infraestructura.repositorios import RepositorioSagaSQL, RepositorioSagaLogSQL
from ..config.database import get_db_session

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

# Dependencia para obtener el servicio de saga
def get_servicio_saga():
    """Dependencia para obtener el servicio de saga configurado"""
    # Obtener sesión de base de datos
    session = next(get_db_session())
    
    # Configurar repositorios
    repositorio_saga = RepositorioSagaSQL(session)
    repositorio_log = RepositorioSagaLogSQL(session)
    
    # Crear servicio de aplicación
    return ServicioSagaOrquestador(repositorio_saga, repositorio_log)

# Modelos Pydantic para requests
class CrearSagaRequest(BaseModel):
    tipo_saga: str = Field(..., description="Tipo de saga a crear")
    id_partner: str = Field(..., description="ID del partner")
    id_campana: str = Field(..., description="ID de la campaña")
    id_conversion: str = Field(..., description="ID de la conversión")
    tipo_conversion: str = Field(..., description="Tipo de conversión")
    informacion_monetaria: Dict[str, Any] = Field(..., description="Información monetaria")
    metadata_cliente: Dict[str, Any] = Field(..., description="Metadata del cliente")
    id_embajador: str = Field(..., description="ID del embajador")
    email_referido: str = Field(..., description="Email del referido")
    valor_conversion: float = Field(..., description="Valor de la conversión")
    porcentaje_comision: float = Field(default=5.0, description="Porcentaje de comisión")
    id_afiliado: str = Field(..., description="ID del afiliado")
    comision: float = Field(..., description="Comisión a pagar")
    metodo_pago: str = Field(default="TRANSFERENCIA_BANCARIA", description="Método de pago")

class EjecutarSagaRequest(BaseModel):
    id_saga: str = Field(..., description="ID de la saga a ejecutar")

# Modelos Pydantic para responses
class SagaResponse(BaseModel):
    id_saga: str
    tipo: str
    estado: str
    timestamp_inicio: str
    timestamp_fin: Optional[str] = None
    error_global: Optional[str] = None
    pasos: List[Dict[str, Any]]

class SagaLogResponse(BaseModel):
    id: str
    evento: str
    datos: Dict[str, Any]
    timestamp: str
    nivel: str

class EstadisticasSagaResponse(BaseModel):
    total_sagas: int
    sagas_completadas: int
    sagas_fallidas: int
    sagas_compensadas: int
    sagas_en_progreso: int
    tasa_exito: float

# Endpoints

@router.post("/saga/crear", response_model=Dict[str, str], status_code=status.HTTP_201_CREATED)
async def crear_saga(
    request: CrearSagaRequest,
    servicio: ServicioSagaOrquestador = Depends(get_servicio_saga)
):
    """Crear una nueva saga de procesamiento de conversión"""
    try:
        datos_contexto = {
            "id_partner": request.id_partner,
            "id_campana": request.id_campana,
            "id_conversion": request.id_conversion,
            "tipo_conversion": request.tipo_conversion,
            "informacion_monetaria": request.informacion_monetaria,
            "metadata_cliente": request.metadata_cliente,
            "id_embajador": request.id_embajador,
            "email_referido": request.email_referido,
            "valor_conversion": request.valor_conversion,
            "porcentaje_comision": request.porcentaje_comision,
            "id_afiliado": request.id_afiliado,
            "comision": request.comision,
            "metodo_pago": request.metodo_pago
        }
        
        id_saga = servicio.crear_saga_procesamiento_conversion(datos_contexto)
        
        return {
            "id_saga": id_saga,
            "mensaje": "Saga creada exitosamente",
            "tipo": "PROCESAMIENTO_CONVERSION",
            "estado": "INICIADA"
        }
        
    except Exception as e:
        logger.error(f"Error creando saga: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/saga/ejecutar", response_model=Dict[str, Any])
async def ejecutar_saga(
    request: EjecutarSagaRequest,
    servicio: ServicioSagaOrquestador = Depends(get_servicio_saga)
):
    """Ejecutar una saga existente"""
    try:
        exito = servicio.ejecutar_saga(request.id_saga)
        
        if exito:
            return {
                "id_saga": request.id_saga,
                "exitoso": True,
                "mensaje": "Saga ejecutada exitosamente",
                "estado": "COMPLETADA"
            }
        else:
            return {
                "id_saga": request.id_saga,
                "exitoso": False,
                "mensaje": "Saga falló, compensación ejecutada",
                "estado": "COMPENSADA"
            }
        
    except Exception as e:
        logger.error(f"Error ejecutando saga: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/saga/{id_saga}/estado", response_model=SagaResponse)
async def obtener_estado_saga(
    id_saga: str,
    servicio: ServicioSagaOrquestador = Depends(get_servicio_saga)
):
    """Obtener el estado actual de una saga"""
    try:
        estado = servicio.obtener_estado_saga(id_saga)
        
        if not estado:
            raise HTTPException(status_code=404, detail="Saga no encontrada")
        
        return SagaResponse(**estado)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado de saga: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/saga/{id_saga}/log", response_model=List[SagaLogResponse])
async def obtener_log_saga(
    id_saga: str,
    servicio: ServicioSagaOrquestador = Depends(get_servicio_saga)
):
    """Obtener el log completo de una saga"""
    try:
        logs = servicio.obtener_log_saga(id_saga)
        
        if not logs:
            raise HTTPException(status_code=404, detail="Log de saga no encontrado")
        
        return [SagaLogResponse(**log) for log in logs]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo log de saga: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/saga/estadisticas", response_model=EstadisticasSagaResponse)
async def obtener_estadisticas_sagas(
    servicio: ServicioSagaOrquestador = Depends(get_servicio_saga)
):
    """Obtener estadísticas de sagas"""
    try:
        # Obtener todas las sagas
        todas_sagas = servicio.repositorio_saga.obtener_todas()
        
        total_sagas = len(todas_sagas)
        sagas_completadas = len([s for s in todas_sagas if s.estado.value == "COMPLETADA"])
        sagas_fallidas = len([s for s in todas_sagas if s.estado.value == "FALLIDA"])
        sagas_compensadas = len([s for s in todas_sagas if s.estado.value == "COMPENSADA"])
        sagas_en_progreso = len([s for s in todas_sagas if s.estado.value in ["INICIADA", "EN_PROGRESO", "COMPENSANDO"]])
        
        tasa_exito = (sagas_completadas / total_sagas * 100) if total_sagas > 0 else 0
        
        return EstadisticasSagaResponse(
            total_sagas=total_sagas,
            sagas_completadas=sagas_completadas,
            sagas_fallidas=sagas_fallidas,
            sagas_compensadas=sagas_compensadas,
            sagas_en_progreso=sagas_en_progreso,
            tasa_exito=round(tasa_exito, 2)
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/saga/demo/exitoso", response_model=Dict[str, Any])
async def demo_saga_exitosa(
    servicio: ServicioSagaOrquestador = Depends(get_servicio_saga)
):
    """Demo de una saga exitosa"""
    try:
        # Crear saga con datos de prueba
        datos_contexto = {
            "id_partner": "partner_demo_001",
            "id_campana": "campana_demo_001",
            "id_conversion": "conversion_demo_001",
            "tipo_conversion": "VENTA",
            "informacion_monetaria": {"valor": 100.0, "moneda": "USD"},
            "metadata_cliente": {"ip": "192.168.1.1", "user_agent": "Demo Browser"},
            "id_embajador": "embajador_demo_001",
            "email_referido": "referido@demo.com",
            "valor_conversion": 100.0,
            "porcentaje_comision": 5.0,
            "id_afiliado": "afiliado_demo_001",
            "comision": 5.0,
            "metodo_pago": "TRANSFERENCIA_BANCARIA"
        }
        
        # Crear saga
        id_saga = servicio.crear_saga_procesamiento_conversion(datos_contexto)
        
        # Ejecutar saga (modificar temporalmente para éxito)
        servicio._simular_exito_servicio = lambda s, a: True  # Forzar éxito
        exito = servicio.ejecutar_saga(id_saga)
        
        return {
            "id_saga": id_saga,
            "exitoso": exito,
            "mensaje": "Demo de saga exitosa completada",
            "datos_contexto": datos_contexto
        }
        
    except Exception as e:
        logger.error(f"Error en demo exitosa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/saga/demo/fallo", response_model=Dict[str, Any])
async def demo_saga_con_fallo(
    servicio: ServicioSagaOrquestador = Depends(get_servicio_saga)
):
    """Demo de una saga con fallo y compensación"""
    try:
        # Crear saga con datos de prueba
        datos_contexto = {
            "id_partner": "partner_demo_002",
            "id_campana": "campana_demo_002",
            "id_conversion": "conversion_demo_002",
            "tipo_conversion": "VENTA",
            "informacion_monetaria": {"valor": 200.0, "moneda": "USD"},
            "metadata_cliente": {"ip": "192.168.1.2", "user_agent": "Demo Browser"},
            "id_embajador": "embajador_demo_002",
            "email_referido": "referido2@demo.com",
            "valor_conversion": 200.0,
            "porcentaje_comision": 5.0,
            "id_afiliado": "afiliado_demo_002",
            "comision": 10.0,
            "metodo_pago": "TRANSFERENCIA_BANCARIA"
        }
        
        # Crear saga
        id_saga = servicio.crear_saga_procesamiento_conversion(datos_contexto)
        
        # Ejecutar saga (con fallo simulado)
        exito = servicio.ejecutar_saga(id_saga)
        
        return {
            "id_saga": id_saga,
            "exitoso": exito,
            "mensaje": "Demo de saga con fallo y compensación completada",
            "datos_contexto": datos_contexto
        }
        
    except Exception as e:
        logger.error(f"Error en demo con fallo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

