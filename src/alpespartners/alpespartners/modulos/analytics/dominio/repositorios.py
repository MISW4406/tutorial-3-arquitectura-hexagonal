from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from .entidades import MetricaPartner, MetricaCampana

class RepositorioMetricas(ABC):
    @abstractmethod
    def obtener_metricas_partner(self, id_partner: str) -> Optional[MetricaPartner]:
        """Obtiene las métricas de un partner"""
        ...
    
    @abstractmethod
    def obtener_metricas_campana(self, id_campana: str) -> Optional[MetricaCampana]:
        """Obtiene las métricas de una campaña específica"""
        ...
    
    @abstractmethod
    def guardar_metricas_partner(self, metricas: MetricaPartner) -> None:
        """Guarda o actualiza las métricas de un partner"""
        ...
    
    @abstractmethod
    def obtener_todas_metricas(self) -> List[MetricaPartner]:
        """Obtiene todas las métricas"""
        ...
