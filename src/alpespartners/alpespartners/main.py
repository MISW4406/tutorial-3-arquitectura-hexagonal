import os
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import threading
import time

from alpespartners.api.tracking import router as tracking_router
from alpespartners.api.loyalty import router as loyalty_router
from alpespartners.api.pagos import router as pagos_router
from alpespartners.api.afiliados import router as afiliados_router
from alpespartners.api.saga import router as saga_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INICIANDO LIFESPAN...")
    
    def iniciar_consumidor():
        print("THREAD CONSUMIDOR: Esperando 3 segundos...")
        time.sleep(3)
        try:
            print("THREAD CONSUMIDOR: Importando módulos...")
            from alpespartners.config.database import get_db_session
            from alpespartners.modulos.tracking.infraestructura.repositorios_sql import (
                RepositorioClicksSQL, RepositorioConversionesSQL
            )
            from alpespartners.modulos.tracking.infraestructura.despachadores import DespachadorEventosPulsar
            from alpespartners.modulos.tracking.aplicacion.servicios import ServicioTracking
            from alpespartners.modulos.tracking.infraestructura.consumidores import ConsumidorComandosTracking
            
            print("THREAD CONSUMIDOR: Configurando dependencias...")
            session = next(get_db_session())
            repo_clicks = RepositorioClicksSQL(session)
            repo_conversiones = RepositorioConversionesSQL(session)
            despachador = DespachadorEventosPulsar()
            
            servicio_tracking = ServicioTracking(repo_clicks, repo_conversiones, despachador)
            
            print("THREAD CONSUMIDOR: Iniciando consumidor...")
            consumidor = ConsumidorComandosTracking(servicio_tracking)
            consumidor.iniciar_consumidor()
            
            print("THREAD CONSUMIDOR: COMPLETADO EXITOSAMENTE!")
            
        except Exception as e:
            print(f"THREAD CONSUMIDOR ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Iniciar consumidor en thread
    thread = threading.Thread(target=iniciar_consumidor, daemon=True)
    thread.start()
    print("LIFESPAN: Thread del consumidor iniciado")
    
    yield
    
    print("CERRANDO APLICACIÓN...")

# Crear instancia de FastAPI
app = FastAPI(
    title="Alpes Partners - Microservices with Apache Pulsar",
    description="Sistema de microservicios usando Apache Pulsar para eventos", 
    version="2.0.0",
    lifespan=lifespan
)

# Registrar rutas
app.include_router(tracking_router, prefix="/v1", tags=["tracking"])
app.include_router(loyalty_router, prefix="/v1", tags=["loyalty"])
app.include_router(pagos_router, prefix="/v1", tags=["pagos"])
app.include_router(afiliados_router, prefix="/v1", tags=["afiliados"])
app.include_router(saga_router, prefix="/v1", tags=["saga"])

@app.get("/health")
async def health_check():
    """Health check que incluye verificación de Pulsar"""
    health_status = {
        "status": "healthy", 
        "services": ["tracking", "loyalty", "pagos", "afiliados", "saga"],
        "message": "Alpes Partners microservices POC with Saga Pattern",
        "event_broker": "Apache Pulsar",
        "pulsar_service_url": os.getenv("PULSAR_SERVICE_URL", "pulsar://pulsar:6650"),
        "pulsar_admin_url": os.getenv("PULSAR_ADMIN_URL", "http://pulsar:8080")
    }
    
    try:
        from alpespartners.config.pulsar import get_pulsar_client
        client = get_pulsar_client()
        if client is None:
            health_status["pulsar_status"] = "unavailable"
        else:
            client.close()
            health_status["pulsar_status"] = "connected"
    except Exception as e:
        health_status["pulsar_status"] = f"error: {str(e)}"
    
    return health_status

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "project": "Alpes Partners Microservices Migration",
        "architecture": "Event-Driven Microservices",
        "event_broker": "Apache Pulsar",
        "entrega": "Entrega 4 - POC Arquitectura",
        "microservices": {
            "tracking": "Gestión de clicks, conversiones y atribuciones",
            "loyalty": "Gestión de embajadores y referidos",
            "pagos": "Gestión de pagos y comisiones",
            "afiliados": "Gestión de afiliados y partners",
            "saga": "Orquestación de transacciones distribuidas con patrón Saga"
        },
        "endpoints": {
            "health": "/health",
            "tracking": "/v1/tracking/*",
            "loyalty": "/v1/loyalty/*",
            "pagos": "/v1/pagos/*",
            "afiliados": "/v1/afiliados/*",
            "saga": "/v1/saga/*"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)