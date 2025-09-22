import logging
from typing import Dict, Any, Optional
from datetime import datetime
import requests
import json

from ..dominio.entidades import Saga, Paso
from ..dominio.objetos_valor import TipoSaga, EstadoSaga, EstadoPaso
from ..dominio.repositorios import RepositorioSaga, RepositorioSagaLog

logger = logging.getLogger(__name__)

class ServicioSagaOrquestador:
    """Servicio orquestador para manejar sagas"""
    
    def __init__(self, 
                 repositorio_saga: RepositorioSaga,
                 repositorio_log: RepositorioSagaLog):
        self.repositorio_saga = repositorio_saga
        self.repositorio_log = repositorio_log
        
        # URLs de los servicios (en producción esto vendría de configuración)
        self.servicios_urls = {
            "tracking": "http://localhost:8000",
            "loyalty": "http://localhost:8000", 
            "pagos": "http://localhost:8000",
            "afiliados": "http://localhost:8000"
        }
    
    def crear_saga_procesamiento_conversion(self, datos_contexto: Dict[str, Any]) -> str:
        """Crea una saga para procesar una conversión completa"""
        saga = Saga(
            tipo=TipoSaga.PROCESAMIENTO_CONVERSION,
            estado=EstadoSaga.INICIADA,
            datos_contexto=datos_contexto
        )
        
        # Definir los pasos de la saga
        saga.agregar_paso(1, "tracking", "registrar_conversion", {
            "id_partner": datos_contexto.get("id_partner"),
            "id_campana": datos_contexto.get("id_campana"),
            "tipo_conversion": datos_contexto.get("tipo_conversion"),
            "informacion_monetaria": datos_contexto.get("informacion_monetaria"),
            "metadata_cliente": datos_contexto.get("metadata_cliente")
        })
        
        saga.agregar_paso(2, "loyalty", "registrar_referido", {
            "id_embajador": datos_contexto.get("id_embajador"),
            "email_referido": datos_contexto.get("email_referido"),
            "valor_conversion": datos_contexto.get("valor_conversion", 0),
            "porcentaje_comision": datos_contexto.get("porcentaje_comision", 5.0)
        })
        
        saga.agregar_paso(3, "afiliados", "actualizar_metricas", {
            "id_afiliado": datos_contexto.get("id_afiliado"),
            "valor_conversion": datos_contexto.get("valor_conversion", 0),
            "comision": datos_contexto.get("comision", 0)
        })
        
        saga.agregar_paso(4, "pagos", "crear_pago", {
            "id_embajador": datos_contexto.get("id_embajador"),
            "id_partner": datos_contexto.get("id_partner"),
            "id_conversion": datos_contexto.get("id_conversion"),
            "monto": datos_contexto.get("comision", 0),
            "metodo_pago": datos_contexto.get("metodo_pago", "TRANSFERENCIA_BANCARIA")
        })
        
        # Guardar saga
        self.repositorio_saga.guardar(saga)
        
        # Log del evento
        self.repositorio_log.registrar_evento(saga.id, "SAGA_CREADA", {
            "tipo": saga.tipo.value,
            "pasos": len(saga.pasos),
            "datos_contexto": saga.datos_contexto
        })
        
        logger.info(f"Saga creada: {saga.id} de tipo {saga.tipo.value}")
        return saga.id
    
    def ejecutar_saga(self, id_saga: str) -> bool:
        """Ejecuta una saga paso a paso"""
        saga = self.repositorio_saga.obtener_por_id(id_saga)
        if not saga:
            logger.error(f"Saga no encontrada: {id_saga}")
            return False
        
        try:
            saga.marcar_en_progreso()
            self.repositorio_saga.guardar(saga)
            self.repositorio_log.registrar_evento(id_saga, "SAGA_INICIADA", {"estado": saga.estado.value})
            
            # Ejecutar pasos secuencialmente
            for paso in sorted(saga.pasos, key=lambda p: p.orden):
                if paso.estado == EstadoPaso.PENDIENTE:
                    exito = self._ejecutar_paso(paso, saga)
                    if not exito:
                        # Si falla un paso, iniciar compensación
                        self._iniciar_compensacion(saga)
                        return False
            
            # Si todos los pasos fueron exitosos
            saga.completar()
            self.repositorio_saga.guardar(saga)
            self.repositorio_log.registrar_evento(id_saga, "SAGA_COMPLETADA", {"estado": saga.estado.value})
            
            logger.info(f"Saga completada exitosamente: {id_saga}")
            return True
            
        except Exception as e:
            logger.error(f"Error ejecutando saga {id_saga}: {str(e)}")
            saga.fallar(str(e))
            self.repositorio_saga.guardar(saga)
            self.repositorio_log.registrar_evento(id_saga, "SAGA_FALLIDA", {"error": str(e)})
            return False
    
    def _ejecutar_paso(self, paso: Paso, saga: Saga) -> bool:
        """Ejecuta un paso individual de la saga"""
        try:
            paso.iniciar()
            self.repositorio_saga.guardar(saga)
            
            self.repositorio_log.registrar_evento(saga.id, "PASO_INICIADO", {
                "paso_id": paso.id,
                "servicio": paso.servicio,
                "accion": paso.accion,
                "orden": paso.orden
            })
            
            # Ejecutar la acción según el servicio
            resultado = self._llamar_servicio(paso.servicio, paso.accion, paso.datos_entrada)
            
            if resultado.get("exitoso", False):
                paso.completar(resultado.get("datos", {}))
                self.repositorio_saga.guardar(saga)
                
                self.repositorio_log.registrar_evento(saga.id, "PASO_COMPLETADO", {
                    "paso_id": paso.id,
                    "servicio": paso.servicio,
                    "accion": paso.accion,
                    "resultado": resultado
                })
                return True
            else:
                paso.fallar(resultado.get("error", "Error desconocido"))
                self.repositorio_saga.guardar(saga)
                
                self.repositorio_log.registrar_evento(saga.id, "PASO_FALLIDO", {
                    "paso_id": paso.id,
                    "servicio": paso.servicio,
                    "accion": paso.accion,
                    "error": resultado.get("error")
                })
                return False
                
        except Exception as e:
            logger.error(f"Error ejecutando paso {paso.id}: {str(e)}")
            paso.fallar(str(e))
            self.repositorio_saga.guardar(saga)
            
            self.repositorio_log.registrar_evento(saga.id, "PASO_ERROR", {
                "paso_id": paso.id,
                "servicio": paso.servicio,
                "accion": paso.accion,
                "error": str(e)
            })
            return False
    
    def _llamar_servicio(self, servicio: str, accion: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Llama a un servicio específico para ejecutar una acción"""
        try:
            url_base = self.servicios_urls.get(servicio)
            if not url_base:
                return {"exitoso": False, "error": f"Servicio no configurado: {servicio}"}
            
            # Mapear acciones a endpoints
            endpoints = {
                "tracking": {
                    "registrar_conversion": "/tracking/conversiones"
                },
                "loyalty": {
                    "registrar_referido": "/loyalty/referidos"
                },
                "afiliados": {
                    "actualizar_metricas": "/afiliados/metricas"  # Endpoint simulado
                },
                "pagos": {
                    "crear_pago": "/pagos"
                }
            }
            
            endpoint = endpoints.get(servicio, {}).get(accion)
            if not endpoint:
                return {"exitoso": False, "error": f"Acción no encontrada: {servicio}.{accion}"}
            
            url = f"{url_base}{endpoint}"
            
            # Simular llamada HTTP (en producción sería real)
            logger.info(f"Llamando a {url} con datos: {datos}")
            
            # Simular respuesta exitosa para demostración
            if self._simular_exito_servicio(servicio, accion):
                return {
                    "exitoso": True,
                    "datos": {
                        "id_generado": f"{servicio}_{accion}_{datetime.now().timestamp()}",
                        "estado": "completado"
                    }
                }
            else:
                return {
                    "exitoso": False,
                    "error": f"Error simulado en {servicio}.{accion}"
                }
                
        except Exception as e:
            logger.error(f"Error llamando servicio {servicio}.{accion}: {str(e)}")
            return {"exitoso": False, "error": str(e)}
    
    def _simular_exito_servicio(self, servicio: str, accion: str) -> bool:
        """Simula el éxito/fallo de servicios para demostración"""
        # Simular fallo en el paso 3 (afiliados) para demostrar compensación
        if servicio == "afiliados" and accion == "actualizar_metricas":
            return False  # Simular fallo para demostrar compensación
        
        # Simular éxito en otros casos
        return True
    
    def _iniciar_compensacion(self, saga: Saga):
        """Inicia el proceso de compensación de una saga"""
        try:
            saga.iniciar_compensacion()
            self.repositorio_saga.guardar(saga)
            
            self.repositorio_log.registrar_evento(saga.id, "COMPENSACION_INICIADA", {
                "pasos_completados": len(saga.obtener_pasos_completados())
            })
            
            # Compensar pasos en orden inverso
            pasos_completados = saga.obtener_pasos_completados()
            for paso in reversed(pasos_completados):
                self._compensar_paso(paso, saga)
            
            saga.completar_compensacion()
            self.repositorio_saga.guardar(saga)
            
            self.repositorio_log.registrar_evento(saga.id, "COMPENSACION_COMPLETADA", {
                "estado": saga.estado.value
            })
            
            logger.info(f"Compensación completada para saga: {saga.id}")
            
        except Exception as e:
            logger.error(f"Error en compensación de saga {saga.id}: {str(e)}")
            self.repositorio_log.registrar_evento(saga.id, "COMPENSACION_ERROR", {"error": str(e)})
    
    def _compensar_paso(self, paso: Paso, saga: Saga):
        """Compensa un paso específico"""
        try:
            # Crear datos de compensación basados en el paso
            datos_compensacion = self._generar_datos_compensacion(paso)
            paso.compensar(datos_compensacion)
            
            self.repositorio_saga.guardar(saga)
            
            self.repositorio_log.registrar_evento(saga.id, "PASO_COMPENSADO", {
                "paso_id": paso.id,
                "servicio": paso.servicio,
                "accion": paso.accion,
                "datos_compensacion": datos_compensacion
            })
            
            logger.info(f"Paso compensado: {paso.id} ({paso.servicio}.{paso.accion})")
            
        except Exception as e:
            logger.error(f"Error compensando paso {paso.id}: {str(e)}")
            self.repositorio_log.registrar_evento(saga.id, "COMPENSACION_PASO_ERROR", {
                "paso_id": paso.id,
                "error": str(e)
            })
    
    def _generar_datos_compensacion(self, paso: Paso) -> Dict[str, Any]:
        """Genera datos de compensación para un paso"""
        compensaciones = {
            "tracking": {
                "registrar_conversion": {"accion": "eliminar_conversion", "id_conversion": paso.datos_salida.get("id_conversion")}
            },
            "loyalty": {
                "registrar_referido": {"accion": "eliminar_referido", "id_referido": paso.datos_salida.get("id_referido")}
            },
            "afiliados": {
                "actualizar_metricas": {"accion": "revertir_metricas", "valor_anterior": paso.datos_entrada.get("valor_conversion")}
            },
            "pagos": {
                "crear_pago": {"accion": "revertir_pago", "id_pago": paso.datos_salida.get("id_pago")}
            }
        }
        
        return compensaciones.get(paso.servicio, {}).get(paso.accion, {})
    
    def obtener_estado_saga(self, id_saga: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de una saga"""
        saga = self.repositorio_saga.obtener_por_id(id_saga)
        if not saga:
            return None
        
        return {
            "id_saga": saga.id,
            "tipo": saga.tipo.value,
            "estado": saga.estado.value,
            "timestamp_inicio": saga.timestamp_inicio.isoformat(),
            "timestamp_fin": saga.timestamp_fin.isoformat() if saga.timestamp_fin else None,
            "error_global": saga.error_global,
            "pasos": [
                {
                    "id": paso.id,
                    "orden": paso.orden,
                    "servicio": paso.servicio,
                    "accion": paso.accion,
                    "estado": paso.estado.value,
                    "timestamp_inicio": paso.timestamp_inicio.isoformat() if paso.timestamp_inicio else None,
                    "timestamp_fin": paso.timestamp_fin.isoformat() if paso.timestamp_fin else None,
                    "error": paso.error,
                    "compensacion": {
                        "servicio": paso.compensacion.servicio,
                        "accion": paso.compensacion.accion,
                        "exitoso": paso.compensacion.exitoso,
                        "timestamp": paso.compensacion.timestamp.isoformat() if paso.compensacion else None
                    } if paso.compensacion else None
                }
                for paso in saga.pasos
            ]
        }
    
    def obtener_log_saga(self, id_saga: str) -> List[Dict[str, Any]]:
        """Obtiene el log completo de una saga"""
        return self.repositorio_log.obtener_log_saga(id_saga)

