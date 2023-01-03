"""Entidades del dominio de vuelos

En este archivo usted encontrará las entidades del dominio de vuelos

"""

from __future__ import annotations
from dataclasses import dataclass, field

import aeroalpes.modulos.vuelos.dominio.objetos_valor as ov
from aeroalpes.seedwork.dominio.entidades import Locacion, AgregacionRaiz, Entidad

@dataclass
class Aeropuerto(Locacion):
    codigo: ov.Codigo = field(default_factory=ov.Codigo)
    nombre: ov.NombreAero = field(default_factory=ov.NombreAero)

    def __str__(self) -> str:
        return self.codigo.codigo.upper()

@dataclass
class Proveedor(Entidad):
    codigo: ov.Codigo = field(default_factory=ov.Codigo)
    nombre: ov.NombreAero = field(default_factory=ov.NombreAero)
    itinerarios: list[ov.Itinerario] = field(default_factory=list[ov.Itinerario])

    def obtener_itinerarios(self, odos: list[Odo], parametros: ParametroBusca):
        return self.itinerarios

@dataclass
class Pasajero(Entidad):
    clase: ov.Clase = field(default_factory=ov.Clase)
    tipo: ov.TipoPasajero = field(default_factory=ov.TipoPasajero)


@dataclass
class Reserva(AgregacionRaiz):
    id_cliente: uuid.UUID = field(hash=True)
    estado: ov.EstadoReserva = field(default_factory=ov.EstadoReserva)
    itinerarios: list[ov.Itinerario] = field(default_factory=list[ov.Itinerario])
