import json
import logging
from datetime import datetime
from typing import Dict, Any

from ...loyalty.dominio.eventos import ReferidoRegistrado
from ..aplicacion.comandos import ComandoCrearPago
from ..aplicacion.servicios import ServicioPagos
from ..dominio.objetos_valor import MetodoPago

logger = logging.getLogger(__name__)

class ConsumidorReferidosRegistrados:
    """Consumidor para eventos de referidos registrados desde el servicio de lealtad"""
    
    def __init__(self, servicio_pagos: ServicioPagos):
        self.servicio_pagos = servicio_pagos
    
    def procesar_evento(self, evento_data: Dict[str, Any]) -> None:
        """Procesa un evento de referido registrado"""
        try:
            # Crear comando para procesar el pago de comisión
            comando = ComandoCrearPago(
                id_embajador=evento_data['id_embajador'],
                id_partner=evento_data['id_partner'],
                id_conversion=evento_data['id_referido'],  # Usar ID del referido como conversión
                monto=evento_data['comision_embajador'],
                moneda="USD",  # Moneda por defecto
                metodo_pago=MetodoPago.TRANSFERENCIA_BANCARIA.value,
                datos_beneficiario={
                    'banco': 'Banco Simulado',
                    'numero_cuenta': f"****{evento_data['id_embajador'][-4:]}",
                    'tipo_cuenta': 'AHORROS'
                },
                referencia=f"COM-{evento_data['id_referido']}",
                descripcion=f"Comisión por referido {evento_data['id_referido']}",
                metadata={
                    'id_referido': evento_data['id_referido'],
                    'email_referido': evento_data['email_referido'],
                    'nombre_referido': evento_data.get('nombre_referido'),
                    'valor_conversion': evento_data['valor_conversion'],
                    'metadata_referido': evento_data.get('metadata_referido', {})
                }
            )
            
            # Procesar el pago
            id_pago = self.servicio_pagos.crear_pago(comando)
            
            logger.info(f"Pago creado exitosamente: {id_pago} para embajador {evento_data['id_embajador']}")
            
        except Exception as e:
            logger.error(f"Error procesando evento de referido registrado: {str(e)}")
            raise

class ConsumidorComandosPago:
    """Consumidor para comandos de pago desde otros servicios"""
    
    def __init__(self, servicio_pagos: ServicioPagos):
        self.servicio_pagos = servicio_pagos
    
    def procesar_comando_crear_pago(self, comando_data: Dict[str, Any]) -> None:
        """Procesa comando de crear pago"""
        try:
            comando = ComandoCrearPago(**comando_data)
            id_pago = self.servicio_pagos.crear_pago(comando)
            logger.info(f"Pago creado desde comando: {id_pago}")
            
        except Exception as e:
            logger.error(f"Error procesando comando crear pago: {str(e)}")
            raise
    
    def procesar_comando_procesar_pago(self, comando_data: Dict[str, Any]) -> None:
        """Procesa comando de procesar pago"""
        try:
            from ..aplicacion.comandos import ComandoProcesarPago
            comando = ComandoProcesarPago(**comando_data)
            resultado = self.servicio_pagos.procesar_pago(comando)
            logger.info(f"Pago procesado: {resultado}")
            
        except Exception as e:
            logger.error(f"Error procesando comando procesar pago: {str(e)}")
            raise
    
    def procesar_comando_revertir_pago(self, comando_data: Dict[str, Any]) -> None:
        """Procesa comando de revertir pago"""
        try:
            from ..aplicacion.comandos import ComandoRevertirPago
            comando = ComandoRevertirPago(**comando_data)
            resultado = self.servicio_pagos.revertir_pago(comando)
            logger.info(f"Pago revertido: {resultado}")
            
        except Exception as e:
            logger.error(f"Error procesando comando revertir pago: {str(e)}")
            raise
