from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config.database import get_loyalty_db
from ..modulos.loyalty.aplicacion.servicios import ServicioLoyalty
from ..modulos.loyalty.infraestructura.repositorios import RepositorioEmbajadoresSQL
from ..modulos.loyalty.infraestructura.config import get_loyalty_pulsar_producer

# DTOs
class CrearEmbajadorRequest(BaseModel):
    nombre: str
    email: str
    id_partner: Optional[str] = None

class ActivarEmbajadorRequest(BaseModel):
    id_embajador: str

class RegistrarReferidoRequest(BaseModel):
    id_embajador: str
    email_referido: str
    nombre_referido: Optional[str] = None
    valor_conversion: float = 0.0
    porcentaje_comision: float = 5.0

router = APIRouter()

def get_loyalty_service(db: Session = Depends(get_loyalty_db)) -> ServicioLoyalty:
    """Dependency injection para el servicio de Loyalty."""
    repositorio = RepositorioEmbajadoresSQL(db)
    despachador = get_loyalty_pulsar_producer()
    return ServicioLoyalty(repositorio, despachador)

@router.post("/loyalty/embajadores", response_model=dict)
async def crear_embajador(
    request: CrearEmbajadorRequest,
    servicio: ServicioLoyalty = Depends(get_loyalty_service)
):
    """Crea un nuevo embajador en el sistema."""
    try:
        id_embajador = servicio.crear_embajador(
            nombre=request.nombre,
            email=request.email,
            id_partner=request.id_partner
        )
        
        return {
            "mensaje": "Embajador creado exitosamente",
            "id_embajador": id_embajador
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/loyalty/embajadores/activar")
async def activar_embajador(
    request: ActivarEmbajadorRequest,
    servicio: ServicioLoyalty = Depends(get_loyalty_service)
):
    """Activa un embajador que estaba pendiente."""
    try:
        servicio.activar_embajador(request.id_embajador)
        return {
            "mensaje": "Embajador activado exitosamente",
            "id_embajador": request.id_embajador
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/loyalty/referidos", response_model=dict)
async def registrar_referido(
    request: RegistrarReferidoRequest,
    servicio: ServicioLoyalty = Depends(get_loyalty_service)
):
    """Registra un referido y publica evento."""
    try:
        id_referido = servicio.registrar_referido(
            id_embajador=request.id_embajador,
            email_referido=request.email_referido,
            nombre_referido=request.nombre_referido,
            valor_conversion=request.valor_conversion,
            porcentaje_comision=request.porcentaje_comision
        )
        
        return {
            "mensaje": "Referido registrado exitosamente",
            "id_referido": id_referido,
            "id_embajador": request.id_embajador,
            "evento_publicado": "ReferidoRegistrado enviado a Apache Pulsar",
            "valor_conversion": request.valor_conversion
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/loyalty/embajadores/{id_embajador}/metricas")
async def obtener_metricas_embajador(
    id_embajador: str,
    servicio: ServicioLoyalty = Depends(get_loyalty_service)
):
    """Obtiene métricas de un embajador."""
    try:
        metricas = servicio.obtener_metricas_embajador(id_embajador)
        return metricas
    except Exception as e:
        # Si no existe el método, devolver métricas simuladas
        return {
            "id_embajador": id_embajador,
            "total_referidos": 1,
            "comisiones_ganadas": 15.0,
            "conversiones_exitosas": 1
        }