from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..modulos.tracking.aplicacion.servicios import ServicioTracking
from ..modulos.tracking.dominio.objetos_valor import TipoConversion, ModeloAtribucion
from ..modulos.tracking.infraestructura.repositorios_sql import RepositorioClicksSQL, RepositorioConversionesSQL
from ..modulos.tracking.infraestructura.despachadores import crear_despachador_pulsar

# DTOs
class ClickRequest(BaseModel):
    id_partner: str
    id_campana: str
    url_origen: str
    url_destino: str
    metadata_cliente: Dict[str, Any]

class ConversionRequest(BaseModel):
    id_partner: str
    id_campana: str
    tipo_conversion: str
    informacion_monetaria: Dict[str, Any]
    metadata_cliente: Dict[str, Any]
    id_click: Optional[str] = None

router = APIRouter()

def get_tracking_service(db: Session = Depends(get_db)) -> ServicioTracking:
    """Dependency injection para el servicio de Tracking."""
    repo_clicks = RepositorioClicksSQL(db)
    repo_conversiones = RepositorioConversionesSQL(db)
    despachador = crear_despachador_pulsar()
    return ServicioTracking(repo_clicks, repo_conversiones, despachador)

@router.post("/tracking/clicks")
async def registrar_click(
    request: ClickRequest,
    servicio_tracking: ServicioTracking = Depends(get_tracking_service)
) -> Dict[str, str]:
    """Registra un click y publica evento en Pulsar."""
    try:
        id_click = servicio_tracking.registrar_click(
            id_partner=request.id_partner,
            id_campana=request.id_campana,
            url_origen=request.url_origen,
            url_destino=request.url_destino,
            metadata_cliente=request.metadata_cliente
        )
        
        return {
            "id_click": id_click,
            "mensaje": "Click registrado exitosamente",
            "evento_broker": "Apache Pulsar"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tracking/conversiones")
async def registrar_conversion(
    request: ConversionRequest,
    servicio_tracking: ServicioTracking = Depends(get_tracking_service)
) -> Dict[str, str]:
    """Registra una conversión y publica evento en Pulsar."""
    try:
        tipo_map = {
            "VENTA": TipoConversion.VENTA,
            "REGISTRO": TipoConversion.REGISTRO,
            "LEAD": TipoConversion.LEAD
        }
        
        tipo = tipo_map.get(request.tipo_conversion.upper())
        if not tipo:
            raise ValueError(f"Tipo de conversión no válido: {request.tipo_conversion}")
        
        id_conversion = servicio_tracking.registrar_conversion(
            id_partner=request.id_partner,
            id_campana=request.id_campana,
            tipo=tipo,
            informacion_monetaria=request.informacion_monetaria,
            metadata_cliente=request.metadata_cliente,
            id_click=request.id_click
        )
        
        return {
            "id_conversion": id_conversion,
            "mensaje": "Conversión registrada exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tracking/conversiones/{id_partner}")
async def obtener_conversiones_partner(
    id_partner: str,
    servicio_tracking: ServicioTracking = Depends(get_tracking_service)
):
    """Obtiene conversiones de un partner específico."""
    try:
        conversiones = servicio_tracking.obtener_conversiones_partner(id_partner)
        # Convertir entidades a diccionarios para JSON
        conversiones_json = []
        for conversion in conversiones:
            try:
                conversiones_json.append({
                    "id_conversion": getattr(conversion, "id_conversion", ""),
                    "id_partner": getattr(conversion, "id_partner", ""),
                    "id_campana": getattr(conversion, "id_campana", ""),
                    "tipo": str(getattr(conversion, "tipo", "")),
                    "valor": getattr(conversion.informacion_monetaria, "valor", 0) if hasattr(conversion, "informacion_monetaria") else 0,
                    "comision": getattr(conversion.informacion_monetaria, "comision", 0) if hasattr(conversion, "informacion_monetaria") else 0,
                    "id_click": getattr(conversion, "id_click", "")
                })
            except Exception as e:
                # Si hay problemas serializando, agregar versión simple
                conversiones_json.append({
                    "id_conversion": str(conversion),
                    "error": str(e)
                })
        
        return conversiones_json
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tracking/clicks")
async def obtener_clicks_endpoint(
    partner_id: Optional[str] = Query(None, description="ID del partner"),
    limite: int = Query(100, description="Límite de resultados"),
    servicio_tracking: ServicioTracking = Depends(get_tracking_service)
) -> List[Dict[str, Any]]:
    """Obtiene lista de clicks para el BFF"""
    try:
        # Usar servicio para obtener clicks con filtros
        clicks = servicio_tracking.repositorio_clicks.obtener_todos()
        
        # Filtrar por partner si se especifica
        if partner_id:
            clicks = [c for c in clicks if c.id_partner == partner_id]
                
        # Convertir a formato JSON
        clicks_json = []
        for click in clicks:
            clicks_json.append({
                "id": str(click.id),
                "id_partner": click.id_partner,
                "id_campana": click.id_campana,
                "url_origen": click.url_origen,
                "url_destino": click.url_destino,
                "timestamp": click.timestamp.isoformat()
            })
        
        return clicks_json
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo clicks: {str(e)}")
    
@router.get("/tracking/conversiones")
async def obtener_conversiones_endpoint(
    partner_id: Optional[str] = Query(None, description="ID del partner"),
    campana_id: Optional[str] = Query(None, description="ID de la campaña"),
    tipo_conversion: Optional[str] = Query(None, description="Tipo de conversión"),
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicio"),
    fecha_fin: Optional[str] = Query(None, description="Fecha fin"),
    limite: int = Query(100, description="Límite de resultados"),
    servicio_tracking: ServicioTracking = Depends(get_tracking_service)
) -> List[Dict[str, Any]]:
    """Obtiene lista de conversiones para el BFF"""
    try:
        conversiones = servicio_tracking.obtener_conversiones_filtradas(
            partner_id=partner_id,
            campana_id=campana_id,
            tipo_conversion=tipo_conversion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limite=limite
        )
        
        conversiones_json = []
        for conversion in conversiones:
            conversiones_json.append({
                "id": conversion.id,
                "id_partner": conversion.id_partner,
                "id_campana": conversion.id_campana,
                "tipo_conversion": conversion.tipo_conversion.value,
                "valor": float(conversion.informacion_monetaria.valor),
                "moneda": conversion.informacion_monetaria.moneda,
                "timestamp": conversion.timestamp.isoformat()
            })
        
        return conversiones_json
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))