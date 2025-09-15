import json
import logging
from kafka import KafkaConsumer
from datetime import datetime
from sqlalchemy.orm import Session

from ..aplicacion.servicios import ServicioTracking
from ..dominio.objetos_valor import TipoConversion, InformacionMonetaria, MetadataCliente
from .repositorios_sql import RepositorioClicksSQL, RepositorioConversionesSQL
from .despachadores import DespachadorEventosKafka
from ....config.database import get_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsumidorEventosLoyalty:
    """Consumer que escucha eventos del Loyalty Service y los procesa en Tracking Service."""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.consumer = None
        
    def inicializar_consumer(self, bootstrap_servers='kafka:9092'):
        """Inicializa el consumer de Kafka"""
        try:
            self.consumer = KafkaConsumer(
                'loyalty.referidos.eventos',  # Escuchar eventos de referidos
                bootstrap_servers=[bootstrap_servers],
                group_id='tracking_loyalty_consumer_group',
                auto_offset_reset='earliest',  # Leer desde el principio si es nuevo consumer
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),

                consumer_timeout_ms=5000,        # Timeout para evitar bloqueos
                session_timeout_ms=30000,        # Sesión más larga (30 seg)
                heartbeat_interval_ms=10000,     # Heartbeat cada 10 seg
                max_poll_interval_ms=300000,     # Max 5 min entre polls
                request_timeout_ms=40000,        # Request timeout 40 seg
                connections_max_idle_ms=540000,  # Conexiones idle 9 min
            
                # Configuraciones adicionales para estabilidad:
                api_version=(0, 10, 1),          # Versión de API compatible
                security_protocol='PLAINTEXT',   # Protocolo simple
                fetch_min_bytes=1,               # Fetch mínimo
                fetch_max_wait_ms=500,           # Wait máximo para fetch
            )
            logger.info("Consumer de eventos Loyalty inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando consumer: {str(e)}")
            raise

    def procesar_referido_registrado(self, mensaje: dict) -> None:
        """
        Procesa un evento ReferidoRegistrado del Loyalty Service.
        Crea una conversión en el Tracking Service para consolidar métricas.
        """
        try:
            datos_evento = mensaje.get('datos', {})
            
            id_referido = datos_evento.get('id_referido')
            id_embajador = datos_evento.get('id_embajador')
            id_partner = datos_evento.get('id_partner')
            email_referido = datos_evento.get('email_referido')
            nombre_referido = datos_evento.get('nombre_referido', 'Referido Loyalty')
            valor_conversion = datos_evento.get('valor_conversion', 0.0)
            comision_embajador = datos_evento.get('comision_embajador', 0.0)
            timestamp_str = datos_evento.get('timestamp')
            
            if not all([id_referido, id_embajador, email_referido]):
                logger.warning(f"Evento con datos incompletos: {datos_evento}")
                return
            
            db = next(self.db_session_factory())
            
            try:
                repo_clicks = RepositorioClicksSQL(db)
                repo_conversiones = RepositorioConversionesSQL(db)
                servicio_tracking = ServicioTracking(repo_clicks, repo_conversiones, None)
                
                metadata_cliente = MetadataCliente(
                    user_agent=f"Loyalty-Referral-{id_embajador}",
                    ip_address="127.0.0.1",  # Simulada
                    referrer=f"embajador:{id_embajador}",
                    device_info={"type": "loyalty_referral", "source": "embajador"},
                    location_info={"country": "unknown", "source": "loyalty"}
                )
                
                info_monetaria = InformacionMonetaria(
                    valor=valor_conversion,
                    moneda="USD",  
                    comision=comision_embajador,
                    porcentaje_comision=(comision_embajador/valor_conversion*100) if valor_conversion > 0 else 0
                )
                
                # Registrar conversión en Tracking Service
                # Nota: Usamos id_referido como id_click para mantener trazabilidad
                id_conversion = servicio_tracking.registrar_conversion(
                    id_partner=id_partner or "loyalty-partner",
                    id_campana=f"loyalty-campaign-{id_embajador}",  
                    tipo=TipoConversion.REGISTRO, 
                    informacion_monetaria=info_monetaria,
                    metadata_cliente=metadata_cliente,
                    id_click=id_referido
                )
                
                logger.info(
                    f"Referido procesado exitosamente: "
                    f"id_referido={id_referido}, "
                    f"id_conversion={id_conversion}, "
                    f"valor={valor_conversion}, "
                    f"embajador={id_embajador}"
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error procesando evento ReferidoRegistrado: {str(e)}")
            logger.error(f"Datos del evento: {datos_evento}")

    def procesar_eventos(self):
        """
        Loop principal que procesa eventos de Kafka.
        Este método bloquea y procesa eventos continuamente.
        """
        if not self.consumer:
            raise ValueError("Consumer no está inicializado. Llamar inicializar_consumer() primero.")
        
        logger.info("Iniciando procesamiento de eventos de Loyalty Service...")
        
        try:
            for mensaje in self.consumer:
                try:
                    logger.info(f"Evento recibido del topic: {mensaje.topic}")
                    
                    mensaje_data = mensaje.value
                    evento_tipo = mensaje_data.get('evento_tipo')
                    servicio_origen = mensaje_data.get('servicio_origen')
                    
                    if servicio_origen != 'loyalty':
                        logger.debug(f"Ignorando evento de servicio: {servicio_origen}")
                        continue
                    
                    if evento_tipo == 'ReferidoRegistrado':
                        self.procesar_referido_registrado(mensaje_data)
                    else:
                        logger.debug(f"Tipo de evento no manejado: {evento_tipo}")
                        
                except Exception as e:
                    logger.error(f"Error procesando mensaje individual: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Deteniendo consumer por interrupción de usuario...")
        except Exception as e:
            logger.error(f"Error en consumer: {str(e)}")
            raise
        finally:
            if self.consumer:
                self.consumer.close()
                logger.info("Consumer de Kafka cerrado.")


def crear_consumer_loyalty():
    """
    Factory function para crear un consumer de eventos de Loyalty.
    """
    return ConsumidorEventosLoyalty(get_db)


if __name__ == "__main__":
    consumer = crear_consumer_loyalty()
    consumer.inicializar_consumer()
    consumer.procesar_eventos()