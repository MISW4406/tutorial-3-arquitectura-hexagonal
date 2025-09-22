import json
import logging
import pulsar
from datetime import datetime
from typing import Dict, Any

from ....config.pulsar import get_pulsar_client, TOPICS

logger = logging.getLogger(__name__)

class DespachadorEventosPulsar:
    """Despachador que usa Apache Pulsar en lugar de Kafka"""
    
    def __init__(self):
        self.client = get_pulsar_client()
        self.producers = {} 
        
    def _get_producer(self, topic: str):
        """Obtiene o crea un producer para el topic"""
        if topic not in self.producers:
            self.producers[topic] = self.client.create_producer(
                topic,
                send_timeout_millis=30000,
                batching_enabled=True,
                batch_size_bytes=128*1024 
            )
        return self.producers[topic]
    
    def publicar_evento_click(self, evento_click):
        """Publica evento de click registrado"""
        try:
            topic = TOPICS['TRACKING_CLICKS']
            producer = self._get_producer(topic)
            
            mensaje = {
                'evento_tipo': 'ClickRegistrado',
                'servicio_origen': 'tracking',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0',
                'datos': {
                    'id_click': evento_click.id_click,
                    'id_partner': evento_click.id_partner,
                    'id_campana': evento_click.id_campana,
                    'url_origen': evento_click.url_origen,
                    'url_destino': evento_click.url_destino,
                    'timestamp': evento_click.timestamp.isoformat(),
                    'metadata_cliente': evento_click.metadata_cliente.to_dict()
                }
            }
            
            producer.send_async(
                json.dumps(mensaje).encode('utf-8'),
                callback=self._mensaje_enviado_callback
            )
            
            logger.info(f"Evento ClickRegistrado enviado a Pulsar: {evento_click.id_click}")
            
        except Exception as e:
            logger.error(f"Error enviando evento click a Pulsar: {str(e)}")
            raise
    
    def publicar_evento_conversion(self, evento_conversion):
        """Publica evento de conversión registrada"""
        try:
            topic = TOPICS['TRACKING_CONVERSIONES']
            producer = self._get_producer(topic)
            
            mensaje = {
                'evento_tipo': 'ConversionRegistrada',
                'servicio_origen': 'tracking',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0',
                'datos': {
                    'id_conversion': evento_conversion.id_conversion,
                    'id_partner': evento_conversion.id_partner,
                    'id_campana': evento_conversion.id_campana,
                    'tipo_conversion': evento_conversion.tipo.value,
                    'valor': evento_conversion.informacion_monetaria.valor,
                    'moneda': evento_conversion.informacion_monetaria.moneda,
                    'comision': evento_conversion.informacion_monetaria.comision,
                    'porcentaje_comision': evento_conversion.informacion_monetaria.porcentaje_comision,
                    'timestamp': evento_conversion.timestamp.isoformat(),
                    'id_click': evento_conversion.id_click
                }
            }
            
            producer.send_async(
                json.dumps(mensaje).encode('utf-8'),
                callback=self._mensaje_enviado_callback
            )
            
            logger.info(f"Evento ConversionRegistrada enviado a Pulsar: {evento_conversion.id_conversion}")
            
        except Exception as e:
            logger.error(f"Error enviando evento conversión a Pulsar: {str(e)}")
            raise
    
    def publicar_evento_atribucion(self, evento_atribucion):
        """Publica evento de atribución asignada"""
        try:
            topic = TOPICS['TRACKING_ATRIBUCIONES']
            producer = self._get_producer(topic)
            
            mensaje = {
                'evento_tipo': 'AtribucionAsignada',
                'servicio_origen': 'tracking',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0',
                'datos': {
                    'id_atribucion': evento_atribucion.id_atribucion,
                    'id_conversion': evento_atribucion.id_conversion,
                    'id_click': evento_atribucion.id_click,
                    'modelo': evento_atribucion.modelo.value,
                    'porcentaje': evento_atribucion.porcentaje,
                    'timestamp': evento_atribucion.timestamp.isoformat()
                }
            }
            
            producer.send_async(
                json.dumps(mensaje).encode('utf-8'),
                callback=self._mensaje_enviado_callback
            )
            
            logger.info(f"Evento AtribucionAsignada enviado a Pulsar: {evento_atribucion.id_atribucion}")
            
        except Exception as e:
            logger.error(f"Error enviando evento atribución a Pulsar: {str(e)}")
            raise
    
    def _mensaje_enviado_callback(self, result, message_id):
        """Callback cuando un mensaje es enviado exitosamente"""
        logger.debug(f"Mensaje enviado exitosamente con ID: {message_id}")
    
    def close(self):
        """Cierra todos los producers y el cliente"""
        for producer in self.producers.values():
            producer.close()
        self.client.close()

# Factory function para dependency injection
def crear_despachador_pulsar() -> DespachadorEventosPulsar:
    """Factory para crear despachador de eventos Pulsar"""
    return DespachadorEventosPulsar()