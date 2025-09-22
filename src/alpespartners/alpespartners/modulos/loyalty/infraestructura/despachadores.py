import json
import logging
import pulsar
from datetime import datetime

from alpespartners.config.pulsar import get_pulsar_client, TOPICS

logger = logging.getLogger(__name__)

class DespachadorEventosPulsarLoyalty:
    def __init__(self):
        self.client = get_pulsar_client()
        self.producers = {}
        self._producer_errors = {}
        
    def _get_producer(self, topic: str):
        """Obtiene o crea un producer para el topic especificado"""
        if topic in self._producer_errors:
            return None
            
        if topic not in self.producers:
            if self.client is None:
                logger.warning(f"Cliente de Pulsar no disponible para topic: {topic}")
                self._producer_errors[topic] = Exception("Cliente de Pulsar no disponible")
                return None
                
            try:
                self.producers[topic] = self.client.create_producer(topic)
                logger.info(f"Producer creado exitosamente para topic: {topic}")
            except Exception as e:
                logger.error(f"Error creando producer para topic {topic}: {str(e)}")
                self._producer_errors[topic] = e
                return None
                
        return self.producers[topic]
    
    def publicar_evento(self, evento, canal: str = None):
        "Método genérico requerido por ServicioLoyalty"
        try:
            logger.info(f"📤 Publicando evento: {type(evento).__name__}")
            
            if hasattr(evento, "nombre_evento"):
                evento_tipo = evento.nombre_evento
            else:
                evento_tipo = type(evento).__name__
            
            if "Referido" in evento_tipo or "ReferidoRegistrado" in evento_tipo:
                return self.publicar_evento_referido_registrado(evento)
            else:
                return self.publicar_evento_embajador_creado(evento)
                
        except Exception as e:
            logger.error(f"❌ Error publicando evento: {str(e)}")
            return False
    
    def publicar_evento_referido_registrado(self, evento):
        try:
            topic = TOPICS["LOYALTY_REFERIDOS"]
            producer = self._get_producer(topic)
            
            if producer is None:
                logger.warning(f"No se pudo crear producer de Pulsar para topic {topic}, evento no publicado")
                return False
            
            datos_evento = {
                "id_referido": getattr(evento, "id_referido", ""),
                "id_embajador": getattr(evento, "id_embajador", ""),
                "email_referido": getattr(evento, "email_referido", ""),
                "nombre_referido": getattr(evento, "nombre_referido", ""),
                "valor_conversion": getattr(evento, "valor_conversion", 0.0),
                "porcentaje_comision": getattr(evento, "porcentaje_comision", 5.0),
                "timestamp": datetime.utcnow().isoformat(),
                "id_partner": "loyalty-partner"
            }
            
            mensaje = {
                "evento_tipo": "ReferidoRegistrado",
                "servicio_origen": "loyalty",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0",
                "datos": datos_evento
            }
            
            message_id = producer.send(json.dumps(mensaje).encode("utf-8"))
            logger.info(f"📤 ReferidoRegistrado enviado: {datos_evento.get('id_referido')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando evento referido: {str(e)}")
            return False
    
    def publicar_evento_embajador_creado(self, evento):
        # Implementación básica
        logger.info("📤 EmbajadorCreado (simulado)")
        return True
    
    def close(self):
        """Cierra todos los producers y el cliente de Pulsar"""
        try:
            for producer in self.producers.values():
                if producer:
                    producer.close()
            logger.info("Producers de Pulsar cerrados exitosamente")
        except Exception as e:
            logger.error(f"Error cerrando producers de Pulsar: {str(e)}")
        
        try:
            if self.client:
                self.client.close()
                logger.info("Cliente de Pulsar cerrado exitosamente")
        except Exception as e:
            logger.error(f"Error cerrando cliente de Pulsar: {str(e)}")

class FabricaDespachadorLoyalty:
    @staticmethod
    def crear_despachador_pulsar():
        return DespachadorEventosPulsarLoyalty()