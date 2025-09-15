import os
from .despachadores import FabricaDespachadorLoyalty

PULSAR_SERVICE_URL = os.getenv('PULSAR_SERVICE_URL', 'pulsar://pulsar:6650')

def get_loyalty_pulsar_producer():
    """
    Función para obtener el despachador de eventos de Loyalty Service usando Pulsar.
    Usado por dependency injection en FastAPI.
    """
    return FabricaDespachadorLoyalty.crear_despachador_pulsar()

TOPICS = {
    'EMBAJADORES_EVENTOS': 'persistent://public/default/loyalty-embajadores-eventos',
    'REFERIDOS_EVENTOS': 'persistent://public/default/loyalty-referidos-eventos'
}