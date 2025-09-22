from fastapi import FastAPI, Request
import asyncio
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings
from typing import Any
import os

from consumidores import suscribirse_a_topico_partners
from api.v1.router import router as v1
from sse_starlette.sse import EventSourceResponse

class Config(BaseSettings):
    APP_VERSION: str = "1"
    ALPES_PARTNERS_HOST: str = os.getenv("ALPES_PARTNERS_HOST", "localhost")
    ALPES_PARTNERS_PORT: str = os.getenv("ALPES_PARTNERS_PORT", "8000")

settings = Config()
app_configs: dict[str, Any] = {
    "title": "BFF Alpes Partners - Partnership Management Platform",
    "description": "Backend for Frontend para la plataforma de gestión de partnerships",
    "version": "1.0.0"
}

tasks = []
eventos_partners = list()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Suscribirse a eventos de los microservicios
    task1 = asyncio.ensure_future(
        suscribirse_a_topico_partners(
            "eventos-tracking", 
            "alpes-partners-bff", 
            "public/default/eventos-tracking", 
            eventos=eventos_partners
        )
    )
    task2 = asyncio.ensure_future(
        suscribirse_a_topico_partners(
            "eventos-loyalty", 
            "alpes-partners-bff", 
            "public/default/eventos-loyalty", 
            eventos=eventos_partners
        )
    )
    task3 = asyncio.ensure_future(
        suscribirse_a_topico_partners(
            "eventos-pagos", 
            "alpes-partners-bff", 
            "public/default/eventos-pagos", 
            eventos=eventos_partners
        )
    )
    task4 = asyncio.ensure_future(
        suscribirse_a_topico_partners(
            "eventos-afiliados", 
            "alpes-partners-bff", 
            "public/default/eventos-afiliados", 
            eventos=eventos_partners
        )
    )
    
    tasks.extend([task1, task2, task3, task4])
    yield

    for task in tasks:
        task.cancel()

app = FastAPI(lifespan=lifespan, **app_configs)

@app.get('/stream')
async def stream_eventos_partners(request: Request):
    """Stream de eventos en tiempo real para partners"""
    def nuevo_evento():
        global eventos_partners
        return {'data': eventos_partners.pop(), 'event': 'EventoPartnership'}
    
    async def leer_eventos():
        global eventos_partners
        while True:
            if await request.is_disconnected():
                break

            if len(eventos_partners) > 0:
                yield nuevo_evento()

            await asyncio.sleep(0.1)

    return EventSourceResponse(leer_eventos())

@app.get('/health')
async def health_check():
    """Health check del BFF"""
    return {
        "status": "healthy",
        "service": "BFF Alpes Partners",
        "version": settings.APP_VERSION,
        "microservices": ["tracking", "loyalty", "pagos", "afiliados"]
    }

app.include_router(v1, prefix="/v1")