import json
import logging
import pulsar
from typing import Dict, Any

from ...config.pulsar import get_pulsar_client, TOPICS
from .consumidores import ConsumidorReferidosRegistrados, ConsumidorComandosPago
from ..aplicacion.servicios import ServicioPagos

logger = logging.getLogger(__name__)

class ConsumidorPulsarPagos:
    """Consumidor principal de Pulsar para el servicio de pagos"""
    
    def __init__(self, servicio_pagos: ServicioPagos):
        self.servicio_pagos = servicio_pagos
        self.pulsar_client = get_pulsar_client()
        self.consumidor_referidos = ConsumidorReferidosRegistrados(servicio_pagos)
        self.consumidor_comandos = ConsumidorComandosPago(servicio_pagos)
        
        # Configurar consumidores
        self.consumer_referidos = self.pulsar_client.subscribe(
            TOPICS["LOYALTY_REFERIDOS"],
            "pagos-consumer-referidos",
            consumer_type=pulsar.ConsumerType.Shared
        )
        
        self.consumer_comandos = self.pulsar_client.subscribe(
            TOPICS["PAGOS_COMANDOS"],
            "pagos-consumer-comandos",
            consumer_type=pulsar.ConsumerType.Shared
        )
    
    def iniciar_consumo(self) -> None:
        """Inicia el consumo de eventos desde Pulsar"""
        logger.info("Iniciando consumidor de eventos de pagos...")
        
        try:
            while True:
                # Procesar eventos de referidos registrados
                self._procesar_mensaje_referidos()
                
                # Procesar comandos de pago
                self._procesar_mensaje_comandos()
                
        except KeyboardInterrupt:
            logger.info("Deteniendo consumidor de eventos...")
        except Exception as e:
            logger.error(f"Error en el consumidor: {str(e)}")
            raise
        finally:
            self.cerrar()
    
    def _procesar_mensaje_referidos(self) -> None:
        """Procesa mensajes de referidos registrados"""
        try:
            msg = self.consumer_referidos.receive(timeout_millis=1000)
            if msg:
                evento_data = json.loads(msg.data().decode('utf-8'))
                logger.info(f"Procesando evento de referido: {evento_data.get('evento_tipo')}")
                
                self.consumidor_referidos.procesar_evento(evento_data)
                
                # Confirmar mensaje
                self.consumer_referidos.acknowledge(msg)
                
        except pulsar.Timeout:
            # Timeout normal, continuar
            pass
        except Exception as e:
            logger.error(f"Error procesando mensaje de referidos: {str(e)}")
            # En caso de error, no confirmar el mensaje para reintento
    
    def _procesar_mensaje_comandos(self) -> None:
        """Procesa mensajes de comandos de pago"""
        try:
            msg = self.consumer_comandos.receive(timeout_millis=1000)
            if msg:
                comando_data = json.loads(msg.data().decode('utf-8'))
                comando_tipo = comando_data.get('comando_tipo')
                logger.info(f"Procesando comando: {comando_tipo}")
                
                if comando_tipo == 'ComandoCrearPago':
                    self.consumidor_comandos.procesar_comando_crear_pago(comando_data)
                elif comando_tipo == 'ComandoProcesarPago':
                    self.consumidor_comandos.procesar_comando_procesar_pago(comando_data)
                elif comando_tipo == 'ComandoRevertirPago':
                    self.consumidor_comandos.procesar_comando_revertir_pago(comando_data)
                else:
                    logger.warning(f"Tipo de comando no reconocido: {comando_tipo}")
                
                # Confirmar mensaje
                self.consumer_comandos.acknowledge(msg)
                
        except pulsar.Timeout:
            # Timeout normal, continuar
            pass
        except Exception as e:
            logger.error(f"Error procesando mensaje de comandos: {str(e)}")
            # En caso de error, no confirmar el mensaje para reintento
    
    def cerrar(self) -> None:
        """Cierra las conexiones de Pulsar"""
        if hasattr(self, 'consumer_referidos'):
            self.consumer_referidos.close()
        if hasattr(self, 'consumer_comandos'):
            self.consumer_comandos.close()
        if hasattr(self, 'pulsar_client'):
            self.pulsar_client.close()
