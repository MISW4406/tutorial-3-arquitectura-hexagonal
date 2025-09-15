from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

from .entidades import Click, Conversion

class RepositorioClicks(ABC):
    @abstractmethod
    def obtener_por_id(self, id_click: str) -> Click:
        ...

    @abstractmethod
    def obtener_por_partner(self, id_partner: str, desde: datetime = None, hasta: datetime = None) -> List[Click]:
        ...

    @abstractmethod
    def agregar(self, click: Click):
        ...
        
    @abstractmethod
    def actualizar(self, click: Click):
        ...

class RepositorioConversiones(ABC):
    @abstractmethod
    def obtener_por_id(self, id_conversion: str) -> Conversion:
        ...

    @abstractmethod
    def obtener_por_partner(self, id_partner: str, desde: datetime = None, hasta: datetime = None) -> List[Conversion]:
        ...

    @abstractmethod
    def obtener_por_click(self, id_click: str) -> List[Conversion]:
        ...

    @abstractmethod
    def agregar(self, conversion: Conversion):
        ...

    @abstractmethod
    def actualizar(self, conversion: Conversion):
        ...

