from abc import ABC, abstractmethod
from typing import List, Optional
from .entidades import Pago, EventoPago

class RepositorioPagos(ABC):
    """Interfaz para el repositorio de pagos"""
    
    @abstractmethod
    def agregar(self, pago: Pago) -> None:
        """Agrega un nuevo pago"""
        pass
    
    @abstractmethod
    def actualizar(self, pago: Pago) -> None:
        """Actualiza un pago existente"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_pago: str) -> Optional[Pago]:
        """Obtiene un pago por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_embajador(self, id_embajador: str) -> List[Pago]:
        """Obtiene todos los pagos de un embajador"""
        pass
    
    @abstractmethod
    def obtener_por_partner(self, id_partner: str) -> List[Pago]:
        """Obtiene todos los pagos de un partner"""
        pass
    
    @abstractmethod
    def obtener_por_conversion(self, id_conversion: str) -> List[Pago]:
        """Obtiene todos los pagos de una conversión"""
        pass
    
    @abstractmethod
    def obtener_pendientes(self) -> List[Pago]:
        """Obtiene todos los pagos pendientes"""
        pass

class RepositorioEventosPago(ABC):
    """Interfaz para el repositorio de eventos (Event Sourcing)"""
    
    @abstractmethod
    def guardar_evento(self, evento: EventoPago) -> None:
        """Guarda un evento de pago"""
        pass
    
    @abstractmethod
    def obtener_eventos_pago(self, id_pago: str) -> List[EventoPago]:
        """Obtiene todos los eventos de un pago específico"""
        pass
    
    @abstractmethod
    def obtener_eventos_por_tipo(self, tipo_evento: str) -> List[EventoPago]:
        """Obtiene todos los eventos de un tipo específico"""
        pass
    
    @abstractmethod
    def obtener_eventos_desde(self, timestamp_desde: str) -> List[EventoPago]:
        """Obtiene eventos desde una fecha específica"""
        pass

class RepositorioOutbox(ABC):
    """Interfaz para el repositorio Outbox (patrón Outbox)"""
    
    @abstractmethod
    def agregar_evento_outbox(self, evento_id: str, evento_tipo: str, 
                            evento_datos: dict, timestamp: str) -> None:
        """Agrega un evento al outbox"""
        pass
    
    @abstractmethod
    def obtener_eventos_pendientes(self) -> List[dict]:
        """Obtiene eventos pendientes de publicación"""
        pass
    
    @abstractmethod
    def marcar_evento_publicado(self, evento_id: str) -> None:
        """Marca un evento como publicado"""
        pass
    
    @abstractmethod
    def limpiar_eventos_antiguos(self, dias_antiguedad: int) -> None:
        """Limpia eventos antiguos ya publicados"""
        pass
