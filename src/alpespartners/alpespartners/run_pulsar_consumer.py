"""
Consumer que escucha eventos de Loyalty Service usando Apache Pulsar
"""

import os
import sys
import json
import pulsar
import time
import signal
import logging
from datetime import datetime

# Agregar el path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpespartners.config.database import get_db
from alpespartners.modulos.tracking.aplicacion.servicios import ServicioTracking
from alpespartners.modulos.tracking.dominio.objetos_valor import TipoConversion, InformacionMonetaria, MetadataCliente
from alpespartners.modulos.tracking.infraestructura.repositorios_sql import RepositorioClicksSQL, RepositorioConversionesSQL

# Configuración de Pulsar inline
PULSAR_SERVICE_URL = os.getenv('PULSAR_SERVICE_URL', 'pulsar://pulsar:6650')
TOPIC_LOYALTY_REFERIDOS = 'persistent://public/default/loyalty-referidos-eventos'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsumidorEventosLoyaltyPulsar:
    """Consumer que escucha eventos del Loyalty Service usando Apache Pulsar"""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.client = None
        self.consumer = None
        self.running = True
        
    def inicializar_consumer(self):
        """Inicializa el consumer de Pulsar"""
        try:
            logger.info(f"Conectando a Pulsar en: {PULSAR_SERVICE_URL}")
            self.client = pulsar.Client(PULSAR_SERVICE_URL)
            
            # Crear consumer
            self.consumer = self.client.subscribe(
                TOPIC_LOYALTY_REFERIDOS,
                subscription_name='tracking-loyalty-consumer-group',
                consumer_type=pulsar.ConsumerType.Shared,
                schema=pulsar.schema.StringSchema(),
                initial_position=pulsar.InitialPosition.Latest
            )
            
            logger.info("Consumer de Apache Pulsar inicializado correctamente")
            logger.info(f"Topic: {TOPIC_LOYALTY_REFERIDOS}")
            
        except Exception as e:
            logger.error(f"Error inicializando consumer de Pulsar: {str(e)}")
            raise

    def procesar_referido_registrado(self, mensaje_data: dict) -> bool:
        """Procesa un evento ReferidoRegistrado del Loyalty Service"""
        try:
            logger.info("Procesando evento ReferidoRegistrado desde Pulsar...")
            
            datos_evento = mensaje_data.get('datos', {})
            id_referido = datos_evento.get('id_referido')
            id_embajador = datos_evento.get('id_embajador')
            email_referido = datos_evento.get('email_referido')
            valor_conversion = datos_evento.get('valor_conversion', 0.0)
            porcentaje_comision = datos_evento.get('porcentaje_comision', 5.0)
            id_partner = datos_evento.get('id_partner')
            
            logger.info(f"ID Referido: {id_referido}")
            logger.info(f"Embajador: {id_embajador}")
            logger.info(f"Email: {email_referido}")
            logger.info(f"Valor: ${valor_conversion}")
            
            # Crear conversión en Tracking Service
            db = next(self.db_session_factory())
            try:
                repo_conversiones = RepositorioConversionesSQL(db)
                repo_clicks = RepositorioClicksSQL(db)
                
                class DummyDespachador:
                    def publicar_evento_conversion(self, evento):
                        logger.info(f"Evento generado: {evento.nombre_evento}")
                
                despachador = DummyDespachador()
                servicio_tracking = ServicioTracking(repo_clicks, repo_conversiones, despachador)
                
                # Crear objetos valor
                info_monetaria = InformacionMonetaria(
                    valor=float(valor_conversion),
                    moneda="USD",
                    comision=float(valor_conversion) * (float(porcentaje_comision) / 100),
                    porcentaje_comision=float(porcentaje_comision)
                )
                
                metadata_cliente = MetadataCliente(
                    user_agent="loyalty-service-referral",
                    ip_address="internal",
                    referrer=f"embajador-{id_embajador}",
                    device_info={"type": "loyalty", "source": "referral"},
                    location_info={"country": "internal", "city": "system"}
                )
                
                # Registrar conversión
                id_conversion = servicio_tracking.registrar_conversion(
                    id_partner=id_partner or "loyalty-partner",
                    id_campana=f"loyalty-campaign-{id_embajador}",
                    tipo=TipoConversion.REGISTRO,
                    informacion_monetaria=info_monetaria,
                    metadata_cliente=metadata_cliente,
                    id_click=id_referido
                )
                
                logger.info(f"Conversión creada en Tracking: {id_conversion}")
                logger.info("Evento procesado exitosamente!")
                
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error procesando evento ReferidoRegistrado: {str(e)}")
            return False

    def procesar_eventos(self):
        """Loop principal que procesa eventos de Pulsar"""
        if not self.consumer:
            raise ValueError("Consumer no está inicializado")
        
        logger.info("Iniciando procesamiento de eventos desde Apache Pulsar...")
        
        try:
            while self.running:
                try:
                    # Receive message con timeout
                    message = self.consumer.receive(timeout_millis=2000)
                    
                    if message:
                        logger.info("Mensaje recibido desde Pulsar")
                        
                        # Parsear mensaje
                        mensaje_str = message.data().decode('utf-8')
                        mensaje_data = json.loads(mensaje_str)
                        
                        evento_tipo = mensaje_data.get('evento_tipo')
                        servicio_origen = mensaje_data.get('servicio_origen')
                        
                        logger.info(f"Tipo: {evento_tipo}")
                        logger.info(f"Origen: {servicio_origen}")
                        
                        if servicio_origen != 'loyalty':
                            logger.debug(f"Ignorando evento de servicio: {servicio_origen}")
                            self.consumer.acknowledge(message)
                            continue
                        
                        if evento_tipo == 'ReferidoRegistrado':
                            success = self.procesar_referido_registrado(mensaje_data)
                            if success:
                                self.consumer.acknowledge(message)
                                logger.info("Mensaje procesado y acknowledged")
                            else:
                                logger.error("Error procesando mensaje - no acknowledged")
                        else:
                            logger.debug(f"Tipo de evento no manejado: {evento_tipo}")
                            self.consumer.acknowledge(message)
                            
                except pulsar.Timeout:
                    # Timeout normal - continuar
                    continue
                except Exception as e:
                    logger.error(f"Error en loop de mensajes: {str(e)}")
                    time.sleep(1)
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Consumer detenido por usuario")
        finally:
            if self.consumer:
                self.consumer.close()
            if self.client:
                self.client.close()
            logger.info("Consumer de Pulsar cerrado")

def main():
    """Función principal"""
    print("APACHE PULSAR CONSUMER: LOYALTY → TRACKING")
    print("=" * 60)
    
    consumer = ConsumidorEventosLoyaltyPulsar(get_db)
    
    def signal_handler(signum, frame):
        consumer.running = False
        logger.info("Señal recibida, cerrando consumer...")
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        consumer.inicializar_consumer()
        logger.info("Consumer Pulsar listo para eventos de Loyalty")
        logger.info(f"Topic: {TOPIC_LOYALTY_REFERIDOS}")
        logger.info("Eventos esperados: ReferidoRegistrado")
        logger.info("Ctrl+C para parar")
        logger.info("=" * 60)
        
        consumer.procesar_eventos()
        
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        
    logger.info("Consumer finalizado")

if __name__ == "__main__":
    main()