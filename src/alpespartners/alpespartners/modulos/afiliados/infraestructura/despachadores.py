import json
import logging
from typing import List
from datetime import datetime

from ....seedwork.dominio.eventos import Despachador
from ..dominio.eventos import (
    AfiliadoRegistrado,
    AfiliadoActivado,
    AfiliadoSuspendido,
    AfiliadoDesactivado,
    AfiliadoActualizado,
    ConfiguracionAfiliadoActualizada,
    AfiliadoEliminado
)

logger = logging.getLogger(__name__)

class DespachadorEventosAfiliados(Despachador):
    """Despachador específico para eventos de afiliados"""
    
    def __init__(self, pulsar_client, topic_afiliados: str):
        self.pulsar_client = pulsar_client
        self.topic_afiliados = topic_afiliados
        self.producer = None
        self._producer_created = False
        self._producer_error = None
    
    def _ensure_producer(self):
        """Crea el producer de Pulsar si no existe"""
        if self._producer_created:
            return self.producer is not None
        
        if self._producer_error:
            return False
        
        if self.pulsar_client is None:
            logger.warning("Cliente de Pulsar no disponible")
            self._producer_error = Exception("Cliente de Pulsar no disponible")
            return False
            
        try:
            self.producer = self.pulsar_client.create_producer(self.topic_afiliados)
            self._producer_created = True
            logger.info(f"Producer creado exitosamente para topic: {self.topic_afiliados}")
            return True
        except Exception as e:
            self._producer_error = e
            logger.error(f"Error creando producer de Pulsar: {str(e)}")
            return False
    
    def publicar_evento(self, evento):
        """Publica un evento de afiliado a Pulsar"""
        try:
            # Asegurar que el producer existe
            if not self._ensure_producer():
                logger.warning(f"No se pudo crear producer de Pulsar, evento no publicado: {evento.__class__.__name__}")
                return False
            
            # Serializar evento a JSON
            evento_data = self._serializar_evento(evento)
            
            # Publicar a Pulsar
            self.producer.send(
                evento_data.encode('utf-8'),
                properties={
                    'tipo_evento': evento.tipo_evento,
                    'id_evento': evento.id,
                    'fecha': evento.fecha.isoformat(),
                    'version': '1.0'
                }
            )
            
            logger.info(f"Evento {evento.tipo_evento} publicado: {evento.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error publicando evento {evento.tipo_evento}: {str(e)}")
            return False
    
    def publicar_eventos(self, eventos: List):
        """Publica múltiples eventos de afiliados"""
        resultados = []
        for evento in eventos:
            resultado = self.publicar_evento(evento)
            resultados.append(resultado)
        return resultados
    
    def cerrar(self):
        """Cierra el producer de Pulsar"""
        if self.producer:
            try:
                self.producer.close()
                logger.info("Producer de Pulsar cerrado exitosamente")
            except Exception as e:
                logger.error(f"Error cerrando producer de Pulsar: {str(e)}")
    
    def _serializar_evento(self, evento) -> str:
        """Serializa un evento a JSON"""
        def convertir_objetos(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return {k: convertir_objetos(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
            elif isinstance(obj, dict):
                return {k: convertir_objetos(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convertir_objetos(item) for item in obj]
            else:
                return obj
        
        evento_dict = convertir_objetos(evento)
        return json.dumps(evento_dict, ensure_ascii=False, indent=2)
    
    def cerrar(self):
        """Cierra la conexión con Pulsar"""
        if self.producer:
            self.producer.close()

class DespachadorEventosAfiliadosOutbox:
    """Despachador de eventos usando patrón Outbox para consistencia transaccional"""
    
    def __init__(self, session, pulsar_client, topic_afiliados: str):
        self.session = session
        self.despachador = DespachadorEventosAfiliados(pulsar_client, topic_afiliados)
    
    def agregar_evento_outbox(self, evento, id_afiliado: str):
        """Agrega un evento al outbox para publicación posterior"""
        from .modelos import EventoOutboxModel
        
        evento_outbox = EventoOutboxModel(
            id_evento=evento.id,
            tipo_evento=evento.tipo_evento,
            id_agregado=id_afiliado,
            datos_evento=self._serializar_datos_evento(evento),
            fecha_creacion=evento.fecha,
            procesado=False
        )
        
        self.session.add(evento_outbox)
        self.session.commit()
        
        logger.info(f"Evento {evento.tipo_evento} agregado al outbox: {evento.id}")
    
    def procesar_eventos_pendientes(self):
        """Procesa eventos pendientes del outbox"""
        from .modelos import EventoOutboxModel
        
        eventos_pendientes = self.session.query(EventoOutboxModel).filter(
            EventoOutboxModel.procesado == False
        ).limit(100).all()
        
        for evento_outbox in eventos_pendientes:
            try:
                # Reconstruir evento desde datos
                evento = self._deserializar_evento(evento_outbox.datos_evento)
                
                # Publicar a Pulsar
                self.despachador.publicar_evento(evento)
                
                # Marcar como procesado
                evento_outbox.procesado = True
                evento_outbox.fecha_procesamiento = datetime.now()
                
                self.session.commit()
                
                logger.info(f"Evento {evento_outbox.tipo_evento} procesado: {evento_outbox.id_evento}")
                
            except Exception as e:
                logger.error(f"Error procesando evento {evento_outbox.id_evento}: {str(e)}")
                evento_outbox.intentos += 1
                self.session.commit()
    
    def _serializar_datos_evento(self, evento) -> dict:
        """Serializa los datos del evento para almacenamiento"""
        def convertir_objetos(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return {k: convertir_objetos(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
            elif isinstance(obj, dict):
                return {k: convertir_objetos(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convertir_objetos(item) for item in obj]
            else:
                return obj
        
        return convertir_objetos(evento)
    
    def _deserializar_evento(self, datos: dict):
        """Deserializa un evento desde datos almacenados"""
        tipo_evento = datos.get('tipo_evento')
        
        if tipo_evento == 'AfiliadoRegistrado':
            return AfiliadoRegistrado(**datos)
        elif tipo_evento == 'AfiliadoActivado':
            return AfiliadoActivado(**datos)
        elif tipo_evento == 'AfiliadoSuspendido':
            return AfiliadoSuspendido(**datos)
        elif tipo_evento == 'AfiliadoDesactivado':
            return AfiliadoDesactivado(**datos)
        elif tipo_evento == 'AfiliadoActualizado':
            return AfiliadoActualizado(**datos)
        elif tipo_evento == 'ConfiguracionAfiliadoActualizada':
            return ConfiguracionAfiliadoActualizada(**datos)
        elif tipo_evento == 'AfiliadoEliminado':
            return AfiliadoEliminado(**datos)
        else:
            raise ValueError(f"Tipo de evento no soportado: {tipo_evento}")
    
    def cerrar(self):
        """Cierra la conexión con Pulsar"""
        self.despachador.cerrar()