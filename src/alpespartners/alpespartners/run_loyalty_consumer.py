"""
Script para ejecutar el consumer de eventos de Loyalty Service.
Este script escucha eventos ReferidoRegistrado y los procesa en Tracking Service.
"""

import logging
import os
import sys
import time
import signal
from sqlalchemy.orm import Session
from kafka.errors import NoBrokersAvailable, KafkaConnectionError

# Agregar el path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpespartners.config.database import get_db
from alpespartners.modulos.tracking.infraestructura.consumidores import ConsumidorEventosLoyalty

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_kafka(max_attempts=30, delay=2):
    """
    Espera a que Kafka esté disponible antes de inicializar el consumer.
    """
    logger.info(f"Esperando a que Kafka esté disponible (máximo {max_attempts * delay} segundos)...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            # Intentar una conexión simple para verificar disponibilidad
            from kafka import KafkaConsumer
            test_consumer = KafkaConsumer(
                bootstrap_servers=['kafka:9092'],
                consumer_timeout_ms=1000
            )
            test_consumer.close()
            logger.info("Kafka está disponible!")
            return True
            
        except (NoBrokersAvailable, KafkaConnectionError) as e:
            logger.warning(f"Intento {attempt}/{max_attempts} - Kafka no disponible: {str(e)}")
            if attempt < max_attempts:
                time.sleep(delay)
            else:
                logger.error("Kafka no está disponible después de todos los intentos")
                return False
        except Exception as e:
            logger.error(f"Error inesperado verificando Kafka: {str(e)}")
            return False
    
    return False

def main():
    """
    Función principal que ejecuta el consumer de eventos de Loyalty.
    """
    print("Iniciando Consumer de Eventos Loyalty → Tracking")
    print("=" * 60)

    # Esperar a que Kafka esté disponible
    if not wait_for_kafka():
        logger.error("No se puede conectar a Kafka. Abortando.")
        sys.exit(1)
    
    # Crear consumer
    consumer = ConsumidorEventosLoyalty(get_db)
    
    # Configurar manejador de señales para cierre limpio
    def signal_handler(signum, frame):
        print(f"\nRecibida señal {signum}. Cerrando consumer...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("Esperando que Kafka esté disponible...")
        time.sleep(5)
        
        print("Inicializando conexión a Kafka...")
        consumer.inicializar_consumer()
        
        print("Consumer listo. Escuchando eventos de Loyalty Service...")
        print("   - Topic: loyalty.referidos.eventos")
        print("   - Eventos esperados: ReferidoRegistrado")
        print("   - Presiona Ctrl+C para detener")
        print("=" * 60)
        
        # Procesar eventos (este método bloquea)
        consumer.procesar_eventos()
        
    except KeyboardInterrupt:
        print("\nConsumer detenido por el usuario.")
    except Exception as e:
        print(f"\nError fatal: {str(e)}")
        time.sleep(5)
        # Reintentar una vez
        try:
            consumer.procesar_eventos()
        except Exception as e2:
            print(f"Error en reintento: {str(e2)}")
            sys.exit(1)
    finally:
        print("Consumer finalizado.")

if __name__ == "__main__":
    main()