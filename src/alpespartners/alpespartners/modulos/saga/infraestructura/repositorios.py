from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..dominio.entidades import Saga, Paso, PasoCompensacion
from ..dominio.objetos_valor import EstadoSaga, EstadoPaso
from ..dominio.repositorios import RepositorioSaga, RepositorioSagaLog
from .modelos import SagaModel, PasoModel, CompensacionModel, SagaLogModel

class RepositorioSagaSQL(RepositorioSaga):
    """Implementación SQL del repositorio de sagas"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def guardar(self, saga: Saga) -> None:
        """Guarda una saga en la base de datos"""
        # Buscar si ya existe
        modelo_existente = self.session.query(SagaModel).filter_by(id=saga.id).first()
        
        if modelo_existente:
            # Actualizar saga existente
            modelo_existente.estado = saga.estado.value
            modelo_existente.datos_contexto = saga.datos_contexto
            modelo_existente.timestamp_fin = saga.timestamp_fin
            modelo_existente.error_global = saga.error_global
            
            # Actualizar pasos
            for paso in saga.pasos:
                paso_modelo = self.session.query(PasoModel).filter_by(id=paso.id).first()
                if paso_modelo:
                    paso_modelo.estado = paso.estado.value
                    paso_modelo.datos_salida = paso.datos_salida
                    paso_modelo.error = paso.error
                    paso_modelo.timestamp_inicio = paso.timestamp_inicio
                    paso_modelo.timestamp_fin = paso.timestamp_fin
                else:
                    # Crear nuevo paso
                    nuevo_paso = PasoModel(
                        id=paso.id,
                        saga_id=saga.id,
                        orden=paso.orden,
                        servicio=paso.servicio,
                        accion=paso.accion,
                        estado=paso.estado.value,
                        datos_entrada=paso.datos_entrada,
                        datos_salida=paso.datos_salida,
                        error=paso.error,
                        timestamp_inicio=paso.timestamp_inicio,
                        timestamp_fin=paso.timestamp_fin
                    )
                    self.session.add(nuevo_paso)
        else:
            # Crear nueva saga
            nuevo_modelo = SagaModel(
                id=saga.id,
                tipo=saga.tipo.value,
                estado=saga.estado.value,
                datos_contexto=saga.datos_contexto,
                timestamp_inicio=saga.timestamp_inicio,
                timestamp_fin=saga.timestamp_fin,
                error_global=saga.error_global
            )
            self.session.add(nuevo_modelo)
            
            # Crear pasos
            for paso in saga.pasos:
                nuevo_paso = PasoModel(
                    id=paso.id,
                    saga_id=saga.id,
                    orden=paso.orden,
                    servicio=paso.servicio,
                    accion=paso.accion,
                    estado=paso.estado.value,
                    datos_entrada=paso.datos_entrada,
                    datos_salida=paso.datos_salida,
                    error=paso.error,
                    timestamp_inicio=paso.timestamp_inicio,
                    timestamp_fin=paso.timestamp_fin
                )
                self.session.add(nuevo_paso)
        
        self.session.commit()
    
    def obtener_por_id(self, id_saga: str) -> Optional[Saga]:
        """Obtiene una saga por ID"""
        modelo = self.session.query(SagaModel).filter_by(id=id_saga).first()
        if not modelo:
            return None
        
        return self._convertir_modelo_a_entidad(modelo)
    
    def obtener_por_estado(self, estado: str) -> List[Saga]:
        """Obtiene sagas por estado"""
        modelos = self.session.query(SagaModel).filter_by(estado=estado).all()
        return [self._convertir_modelo_a_entidad(modelo) for modelo in modelos]
    
    def obtener_todas(self) -> List[Saga]:
        """Obtiene todas las sagas"""
        modelos = self.session.query(SagaModel).all()
        return [self._convertir_modelo_a_entidad(modelo) for modelo in modelos]
    
    def _convertir_modelo_a_entidad(self, modelo: SagaModel) -> Saga:
        """Convierte un modelo SQL a entidad de dominio"""
        from ..dominio.objetos_valor import TipoSaga
        
        # Convertir pasos
        pasos = []
        for paso_modelo in modelo.pasos:
            paso = Paso(
                id=paso_modelo.id,
                orden=paso_modelo.orden,
                servicio=paso_modelo.servicio,
                accion=paso_modelo.accion,
                estado=EstadoPaso(paso_modelo.estado),
                datos_entrada=paso_modelo.datos_entrada or {},
                datos_salida=paso_modelo.datos_salida,
                error=paso_modelo.error,
                timestamp_inicio=paso_modelo.timestamp_inicio,
                timestamp_fin=paso_modelo.timestamp_fin
            )
            pasos.append(paso)
        
        # Crear saga
        saga = Saga(
            id=modelo.id,
            tipo=TipoSaga(modelo.tipo),
            estado=EstadoSaga(modelo.estado),
            pasos=pasos,
            datos_contexto=modelo.datos_contexto or {},
            timestamp_inicio=modelo.timestamp_inicio,
            timestamp_fin=modelo.timestamp_fin,
            error_global=modelo.error_global
        )
        
        return saga

class RepositorioSagaLogSQL(RepositorioSagaLog):
    """Implementación SQL del repositorio del log de sagas"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def registrar_evento(self, id_saga: str, evento: str, datos: dict) -> None:
        """Registra un evento en el log de la saga"""
        log_entry = SagaLogModel(
            id=f"{id_saga}_{datetime.now().timestamp()}",
            saga_id=id_saga,
            evento=evento,
            datos_evento=datos,
            timestamp=datetime.now()
        )
        self.session.add(log_entry)
        self.session.commit()
    
    def obtener_log_saga(self, id_saga: str) -> List[dict]:
        """Obtiene el log completo de una saga"""
        logs = self.session.query(SagaLogModel).filter_by(saga_id=id_saga).order_by(SagaLogModel.timestamp).all()
        return [
            {
                "id": log.id,
                "evento": log.evento,
                "datos": log.datos_evento,
                "timestamp": log.timestamp.isoformat(),
                "nivel": log.nivel
            }
            for log in logs
        ]
    
    def obtener_logs_por_estado(self, estado: str) -> List[dict]:
        """Obtiene logs de sagas por estado"""
        logs = self.session.query(SagaLogModel).join(SagaModel).filter(SagaModel.estado == estado).order_by(SagaLogModel.timestamp).all()
        return [
            {
                "id": log.id,
                "saga_id": log.saga_id,
                "evento": log.evento,
                "datos": log.datos_evento,
                "timestamp": log.timestamp.isoformat(),
                "nivel": log.nivel
            }
            for log in logs
        ]

