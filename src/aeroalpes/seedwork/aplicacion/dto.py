from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class DTO():
    ...

class Mapeador(ABC):
    @abstractmethod
    def externo_a_dto(self, externo: any) -> DTO:
        ...

    @abstractmethod
    def dto_a_externo(self, dto: DTO) -> any:
        ...
    