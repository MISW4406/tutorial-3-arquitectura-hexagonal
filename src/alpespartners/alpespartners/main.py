import os
from fastapi import FastAPI
import uvicorn

from alpespartners.api.tracking import router as tracking_router
from alpespartners.api.loyalty import router as loyalty_router
from alpespartners.api.pagos import router as pagos_router
from alpespartners.api.afiliados import router as afiliados_router

# Crear instancia de FastAPI
app = FastAPI(
    title="Alpes Partners - Microservices with Apache Pulsar",
    description="Sistema de microservicios usando Apache Pulsar para eventos",
    version="2.0.0"
)

# Registrar rutas
app.include_router(tracking_router, prefix="/v1", tags=["tracking"])
app.include_router(loyalty_router, prefix="/v1", tags=["loyalty"])
app.include_router(pagos_router, prefix="/v1", tags=["pagos"])
app.include_router(afiliados_router, prefix="/v1", tags=["afiliados"])

@app.get("/health")
async def health_check():
    """Health check que incluye verificación de Pulsar"""
    health_status = {
        "status": "healthy", 
        "services": ["tracking", "loyalty", "pagos", "afiliados"],
        "message": "Alpes Partners microservices POC",
        "event_broker": "Apache Pulsar",
        "pulsar_service_url": os.getenv("PULSAR_SERVICE_URL", "pulsar://pulsar:6650"),
        "pulsar_admin_url": os.getenv("PULSAR_ADMIN_URL", "http://pulsar:8080")
    }
    
    # Verificar Pulsar
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
            "pagos": "Gestión de pagos y comisiones"
        },
        "endpoints": {
            "health": "/health",
            "tracking": "/v1/tracking/*",
            "loyalty": "/v1/loyalty/*",
            "pagos": "/v1/pagos/*"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)