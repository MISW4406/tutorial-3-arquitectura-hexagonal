import json
import logging
import os
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from typing import Dict, Any

from ....config.database import get_db
from ..aplicacion.servicios import ServicioAnalytics
from .repositorios import RepositorioMetricasSQL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsumidorEventos:
    def __init__(self, db: Session):
        self.servicio_analytics = ServicioAnalytics(
            repositorio=RepositorioMetricasSQL(db)
        )
        self.consumer = KafkaConsumer(
            'tracking.clicks',
            'tracking.conversiones',
            bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')],
            group_id='analytics_consumer_group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    
    def procesar_click(self, evento: Dict[str, Any]) -> None:
        """Procesa un evento de click"""
        logger.info(f"Procesando click - Partner: {evento['id_partner']}, Campaña: {evento['id_campana']}")
        self.servicio_analytics.procesar_click(
            id_partner=evento['id_partner'],
            id_campana=evento['id_campana']
        )
    
    def procesar_conversion(self, evento: Dict[str, Any]) -> None:
        """Procesa un evento de conversión"""
        logger.info(f"Procesando conversión - Partner: {evento['id_partner']}, Campaña: {evento['id_campana']}")
        info_monetaria = evento['informacion_monetaria']
        self.servicio_analytics.procesar_conversion(
            id_partner=evento['id_partner'],
            id_campana=evento['id_campana'],
            valor=info_monetaria['valor'],
            comision=info_monetaria['comision']
        )
    
    def iniciar(self):
        """Inicia el consumidor de eventos"""
        logger.info("Iniciando consumidor de eventos de analytics...")
        try:
            for message in self.consumer:
                try:
                    if message.topic == 'tracking.clicks':
                        self.procesar_click(message.value)
                    elif message.topic == 'tracking.conversiones':
                        self.procesar_conversion(message.value)
                except Exception as e:
                    logger.error(f"Error procesando mensaje: {str(e)}")
                    continue
        except KeyboardInterrupt:
            logger.info("Deteniendo consumidor de eventos...")
        finally:
            self.consumer.close()
            logger.info("Consumidor de eventos detenido.")
