from abc import ABC, abstractmethod
from typing import List, Optional
from .entidades import Saga

class RepositorioSaga(ABC):
    """Interface para el repositorio de sagas"""
    
    @abstractmethod
    def guardar(self, saga: Saga) -> None:
        """Guarda una saga"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_saga: str) -> Optional[Saga]:
        """Obtiene una saga por ID"""
        pass
    
    @abstractmethod
    def obtener_por_estado(self, estado: str) -> List[Saga]:
        """Obtiene sagas por estado"""
        pass
    
    @abstractmethod
    def obtener_todas(self) -> List[Saga]:
        """Obtiene todas las sagas"""
        pass

class RepositorioSagaLog(ABC):
    """Interface para el repositorio del log de sagas"""
    
    @abstractmethod
    def registrar_evento(self, id_saga: str, evento: str, datos: dict) -> None:
        """Registra un evento en el log de la saga"""
        pass
    
    @abstractmethod
    def obtener_log_saga(self, id_saga: str) -> List[dict]:
        """Obtiene el log completo de una saga"""
        pass
    
    @abstractmethod
    def obtener_logs_por_estado(self, estado: str) -> List[dict]:
        """Obtiene logs de sagas por estado"""
        pass

