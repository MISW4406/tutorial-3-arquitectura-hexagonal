from abc import ABC, abstractmethod
from uuid import UUID
from .entidades import Entidad

class Repositorio(ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID) -> Entidad:
        ...

    @abstractmethod
    def obtener_todos(self, id: UUID) -> list[Entidad]:
        ...

    @abstractmethod
    def agregar(self, entity: Entidad):
        ...

    @abstractmethod
    def actualizar(self, entity: Entidad):
        ...

    @abstractmethod
    def eliminar(self, entity_id: UUID):
        ...

    @staticmethod
    def siguiente_id() -> UUID:
        return UUID.v4()


class Mapeador(ABC):
    @abstractmethod
    def entidad_a_dto(self, entidad: Entidad) -> any:
        ...

    @abstractmethod
    def dto_a_entidad(self, dto: any) -> Entidad:
        ...
    