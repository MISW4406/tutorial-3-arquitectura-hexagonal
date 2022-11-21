from dataclasses import dataclass, field
from aeroalpes.seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class ItinerarioDTO(DTO):
    ...

@dataclass(frozen=True)
class ReservaDTO(DTO):
    itinerarios: list = field(default_factory=list)