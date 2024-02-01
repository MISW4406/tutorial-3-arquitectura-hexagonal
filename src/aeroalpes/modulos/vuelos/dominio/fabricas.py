""" Fábricas para la creación de objetos del dominio de vuelos

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos del dominio de vuelos

"""

from .entidades import Reserva
from .reglas import ReservaValida
from .excepciones import TipoObjetoNoExisteEnDominioVuelosExcepcion
from aeroalpes.seedwork.dominio.repositorios import Mapeador, Repositorio
from aeroalpes.seedwork.dominio.fabricas import Fabrica
from aeroalpes.seedwork.dominio.entidades import Entidad
from dataclasses import dataclass

@dataclass
class _FabricaReserva(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if isinstance(obj, Entidad):
            return mapeador.entidad_a_dto(obj)
        else:
            reserva: Reserva = mapeador.dto_a_entidad(obj)
            self.validar_regla(ReservaValida(reserva))
            
            return reserva

@dataclass
class FabricaVuelos(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if mapeador.obtener_tipo() == Reserva.__class__:
            fabrica_reserva = _FabricaReserva()
            return fabrica_reserva.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioVuelosExcepcion()

