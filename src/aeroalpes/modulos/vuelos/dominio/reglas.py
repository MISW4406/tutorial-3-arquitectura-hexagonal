"""Reglas de negocio del dominio de cliente

En este archivo usted encontrará reglas de negocio del dominio de cliente

"""

from aeroalpes.seedwork.dominio.reglas import ReglaNegocio, ReglaNegocioCompuesta
from .objetos_valor import Leg, Odo, Ruta, Segmento
from .entidades import Pasajero, Reserva
from .objetos_valor import TipoPasajero, Itinerario


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

class _RutaFechasValidas(ReglaNegocio):
    ruta: Ruta

    def __init__(self, ruta, mensaje='Las fechas de la ruta son incorrectas'):
        super().__init__(mensaje)
        self.ruta = ruta

    def es_valido(self) -> bool:
        return self.ruta.fecha_llegada() > self.ruta.fecha_salida()

class _RutaLocalizacionesValidas(ReglaNegocio):
    ruta: Ruta

    def __init__(self, ruta, mensaje='La ruta propuesta es incorrecta'):
        super().__init__(mensaje)
        self.ruta = ruta

    def es_valido(self) -> bool:
        return not (self.ruta.origen() and self.ruta.destino()) or self.ruta.origen() != self.ruta.destino()

class RutaValida(ReglaNegocioCompuesta):
    ruta: Ruta

    def __init__(self, ruta, mensaje='La ruta propuesta es incorrecta'):
        self.ruta = ruta
        
        reglas = [_RutaFechasValidas(self.ruta), _RutaLocalizacionesValidas(self.ruta)]
        super().__init__(mensaje, reglas)



class _MinimoUnLegEnSegmento(ReglaNegocio):
    legs: list[Leg]

    def __init__(self, legs: list[Leg], mensaje='Un segmento debe tener al menos un leg en su lista'):
        super().__init__(mensaje)
        self.legs = legs

    def es_valido(self) -> bool:
        return len(self.legs) > 0 and isinstance(self.legs[0], Leg)

class _MinimoUnSegmentoEnOdo(ReglaNegocio):
    segmentos: list[Segmento]

    def __init__(self, segmentos: list[Odo], mensaje='Un Odo debe tener al menos un segmento en su lista'):
        super().__init__(mensaje)
        self.segmentos = segmentos

    def es_valido(self) -> bool:
        return len(self.segmentos) > 0 and isinstance(self.segmentos[0], Segmento)

class SegmentoValido(ReglaNegocioCompuesta):
    segmento: Segmento

    def __init__(self, segmento: Segmento, mensaje="Segmento inválido"):
        self.segmento = segmento

        reglas = [
            _MinimoUnLegEnSegmento(self.segmento.legs),
            RutaValida(self.segmento, f"Segmento propuesto incorrecto: {str(self.segmento)}"),
        ]
        reglas.extend([RutaValida(leg, f"Leg propuesto incorrecto: {str(leg)}") for leg in self.segmento.legs])
        super().__init__(mensaje, reglas)

class _MinimoUnOdoEnItinerario(ReglaNegocio):
    odos: list[Odo]

    def __init__(self, odos: list[Odo], mensaje='Un itinerario debe tener al menos un odo en su lista'):
        super().__init__(mensaje)
        self.odos = odos

    def es_valido(self) -> bool:
        return len(self.odos) > 0 and isinstance(self.odos[0], Odo)

class OdoValido(ReglaNegocioCompuesta):
    odo: Odo

    def __init__(self, odo: Odo, mensaje='Odo inválido'):
        self.odo = odo

        reglas = [_MinimoUnSegmentoEnOdo(self.odo.segmentos)]
        reglas.extend([SegmentoValido(segmento) for segmento in self.odo.segmentos])
        super(OdoValido, self).__init__(mensaje, reglas)

class _MinimoUnItinerario(ReglaNegocio):
    itinerarios: list[Itinerario]

    def __init__(self, itinerarios, mensaje='La lista de itinerarios debe tener al menos un itinerario'):
        super().__init__(mensaje)
        self.itinerarios = itinerarios

    def es_valido(self) -> bool:
        return len(self.itinerarios) > 0 and isinstance(self.itinerarios[0], Itinerario)

class ItinerarioValido(ReglaNegocioCompuesta):
    itinerario: Itinerario

    def __init__(self, itinerario: Itinerario, mensaje='Itinerario inválido'):
        self.itinerario = itinerario

        reglas = [_MinimoUnOdoEnItinerario(self.itinerario.odos)]
        reglas.extend([OdoValido(odo) for odo in self.itinerario.odos])
        super(ItinerarioValido, self).__init__(mensaje, reglas)

class ReservaValida(ReglaNegocioCompuesta):
    reserva: Reserva

    def __init__(self, reserva: Reserva, mensaje='Reserva inválida'):
        self.reserva = reserva

        reglas = [_MinimoUnItinerario(self.reserva.itinerarios)]
        reglas.extend([ItinerarioValido(itinerario) for itinerario in self.reserva.itinerarios])
        super(ReservaValida, self).__init__(mensaje, reglas)