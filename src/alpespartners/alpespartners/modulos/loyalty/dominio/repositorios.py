from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import Embajador

class RepositorioEmbajadores(ABC):
    @abstractmethod
    def agregar(self, embajador: Embajador) -> None:
        """Persiste un nuevo embajador"""
        ...

    @abstractmethod
    def obtener_por_id(self, id_embajador: str) -> Optional[Embajador]:
        """Obtiene un embajador por su ID único"""
        ...

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Embajador]:
        """Obtiene un embajador por su email"""
        ...

    @abstractmethod
    def obtener_por_partner(self, id_partner: str, activos_solo: bool = False) -> List[Embajador]:
        """Obtiene todos los embajadores asociados a un partner"""
        ...

    @abstractmethod
    def actualizar(self, embajador: Embajador) -> None:
        """Actualiza un embajador existente"""
        ...