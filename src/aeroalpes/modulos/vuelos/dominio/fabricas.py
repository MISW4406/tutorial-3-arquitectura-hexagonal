from .entidades import Reserva
from .excepciones import TipoObjetoNoExisteEnDominioVuelosExcepcion
from dataclasses import dataclass

@dataclass
class _FabricaReserva():
    def crear_objeto(self, obj: Reserva):
        return Reserva()

@dataclass
class FabricaVuelos():
    def crear_objeto(self, obj: any):
        if type(obj) == Reserva.__class__:
            fabrica_reserva = _FabricaReserva()
            return fabrica_reserva.crear_objeto(obj)
        else:
            raise TipoObjetoNoExisteEnDominioVuelosExcepcion()

