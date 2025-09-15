import os
import pulsar

PULSAR_SERVICE_URL = os.getenv("PULSAR_SERVICE_URL", "pulsar://pulsar:6650")
PULSAR_ADMIN_URL = os.getenv("PULSAR_ADMIN_URL", "http://pulsar:8080")

TOPICS = {
    "LOYALTY_REFERIDOS": "persistent://public/default/loyalty-referidos-eventos",
    "PAGOS_EVENTOS": "persistent://public/default/pagos-eventos",
    "PAGOS_COMANDOS": "persistent://public/default/pagos-comandos",
    "AFILIADOS_EVENTOS": "persistent://public/default/afiliados-eventos",
    "AFILIADOS_COMANDOS": "persistent://public/default/afiliados-comandos"
}

def get_pulsar_client():
    """Crea un cliente de Pulsar con configuración de error handling"""
    try:
        client = pulsar.Client(
            PULSAR_SERVICE_URL,
            connection_timeout_ms=5000,  # 5 segundos timeout
            operation_timeout_ms=30000,  # 30 segundos timeout
            keep_alive_interval_ms=30000  # Keep alive cada 30 segundos
        )
        return client
    except Exception as e:
        print(f"Error creando cliente de Pulsar: {str(e)}")
        # Retornar None para que el despachador pueda manejar la ausencia de Pulsar
        return None
