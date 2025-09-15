from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
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