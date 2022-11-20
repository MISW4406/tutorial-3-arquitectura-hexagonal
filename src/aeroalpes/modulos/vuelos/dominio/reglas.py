
from aeroalpes.seedwork.dominio.reglas import ReglaNegocio
from .objetos_valor import Ruta
from .entidades import Pasajero
from .objetos_valor import TipoPasajero


class MinimoUnAdulto(ReglaNegocio):

    pasajeros: list[Pasajero]

    def __init__(self, pasajeros, mensaje='Al menos un adulto debe ser parte del itinerario'):
        super().__init__(mensaje)
        self.pasajeros = pasajeros

    def es_valido(self) -> bool:
        for pasajero in self.pasajeros:
            if pasajero.tipo == TipoPasajero.ADULTO:
                return True
        return False

class RutaValida(ReglaNegocio):

    ruta: Ruta

    def __init__(self, ruta, mensaje='La ruta propuesta es incorrecta'):
        super().__init__(mensaje)
        self.ruta = ruta

    def es_valido(self) -> bool:
        return self.ruta.destino != self.ruta.origen