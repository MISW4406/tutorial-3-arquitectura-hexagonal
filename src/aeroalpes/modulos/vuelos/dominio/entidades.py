from __future__ import annotations
from dataclasses import dataclass, field
from .objetos_valor import Codigo, Odo, ParametroBusca, TipoVuelo, NombreAero, Clase, TipoPasajero, Itinerario
from aeroalpes.seedwork.dominio.entidades import Locacion, AgregacionRaiz, Entidad

@dataclass
class Aeropuerto(Locacion):
    codigo: Codigo = field(default_factory=Codigo)
    nombre: NombreAero = field(default_factory=NombreAero)

    def __str__(self) -> str:
        return self.codigo.codigo.upper()

@dataclass
class Proveedor(Entidad):
    codigo: Codigo = field(default_factory=Codigo)
    nombre: NombreAero = field(default_factory=NombreAero)
    itinerarios: list[Itinerario] = field(default_factory=list)

    def obtener_itinerarios(self, odos: list[Odo], parametros: ParametroBusca):
        return self.itinerarios

@dataclass
class Pasajero(Entidad):
    clase: Clase = field(default_factory=Clase)
    tipo: TipoPasajero = field(default_factory=TipoPasajero)


@dataclass
class Reserva(AgregacionRaiz):
    itinerarios: list[Itinerario] = field(default_factory=list[Itinerario])