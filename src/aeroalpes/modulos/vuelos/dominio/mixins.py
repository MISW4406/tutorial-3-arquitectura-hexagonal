"""Mixins del dominio de vuelos

En este archivo usted encontrará las Mixins con capacidades 
reusables en el dominio de vuelos

"""

from .entidades import Itinerario

class FiltradoItinerariosMixin:

    def filtrar_mejores_itinerarios(self, itinerarios: list[Itinerario]) -> list[Itinerario]:
        # Logica compleja para filtrar itinerarios
        # TODO
        return itinerarios