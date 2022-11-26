from dataclasses import dataclass, field
from aeroalpes.seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class LegDTO(DTO):
    fecha_salida: str
    fecha_llegada: str
    origen: dict
    destino: dict

@dataclass(frozen=True)
class SegmentoDTO(DTO):
    legs: list[LegDTO]

@dataclass(frozen=True)
class OdoDTO(DTO):
    segmentos: list[SegmentoDTO]

@dataclass(frozen=True)
class ItinerarioDTO(DTO):
    odos: list[OdoDTO]

@dataclass(frozen=True)
class ReservaDTO(DTO):
    fecha_creacion: str = field(default_factory=str)
    fecha_actualizacion: str = field(default_factory=str)
    id: str = field(default_factory=str)
    itinerarios: list[ItinerarioDTO] = field(default_factory=list)