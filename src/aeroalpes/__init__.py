from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

class TocinoBase(ABC):
    @abstractmethod
    def satisface(self, obj: Any) -> bool:
        raise NotImplementedError()

    def __call__(self, obj: Any) -> bool:
        return self.satisface(obj)

    def __and__(self, otro: "TocinoBase") -> "And":
        return And(self, otro)

    def __or__(self, otro: "TocinoBase") -> "Or":
        return Or(self, otro)

    def __neg__(self) -> "TocinoBase":
        return Not(self)

@dataclass(frozen=True)
class And(TocinoBase):
    primero: TocinoBase
    segundo: TocinoBase

    def satisface(self, obj: Any) -> bool:
        return self.primero.satisface(obj) and self.segundo.satisface(obj)

@dataclass(frozen=True)
class Or(TocinoBase):
    primero: TocinoBase
    segundo: TocinoBase

    def satisface(self, obj: Any) -> bool:
        return self.primero.satisface(obj) or self.segundo.satisface(obj)

@dataclass(frozen=True)
class Not(TocinoBase):
    sujeto: TocinoBase

    def satisface(self, obj: Any) -> bool:
        return not self.sujeto.satisface(obj)
