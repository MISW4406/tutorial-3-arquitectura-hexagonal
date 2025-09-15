from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

class IPuertoRegistrarClick(ABC):
    @abstractmethod
    def ejecutar(self, 
                 id_partner: str,
                 id_campana: str,
                 url_origen: str,
                 url_destino: str,
                 metadata_cliente: Dict) -> str:
        """Puerto para registrar un click"""
        ...

class IPuertoRegistrarConversion(ABC):
    @abstractmethod
    def ejecutar(self,
                 id_partner: str,
                 id_campana: str,
                 tipo_conversion: str,
                 informacion_monetaria: Dict,
                 metadata_cliente: Dict,
                 id_click: Optional[str] = None) -> str:
        """Puerto para registrar una conversión"""
        ...

class IPuertoAsignarAtribucion(ABC):
    @abstractmethod
    def ejecutar(self,
                 id_conversion: str,
                 modelo: str,
                 porcentaje: float,
                 ventana_atribucion: int) -> None:
        """Puerto para asignar una atribución"""
        ...

class IPuertoConsultarConversiones(ABC):
    @abstractmethod
    def ejecutar(self,
                 id_partner: str,
                 desde: Optional[datetime] = None,
                 hasta: Optional[datetime] = None) -> List[Dict]:
        """Puerto para consultar conversiones"""
        ...
