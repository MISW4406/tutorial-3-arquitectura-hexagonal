from aeroalpes.seedwork.aplicacion.dto import Mapeador
from aeroalpes.modulos.vuelos.dominio.entidades import Reserva
from aeroalpes.modulos.vuelos.dominio.objetos_valor import Itinerario
from .dto import ReservaDTO, ItinerarioDTO

class MapeadorReservaDTOJson(Mapeador):
    def _procesar_itinerario(self, itinerario: Itinerario) -> ItinerarioDTO:
        dto: ItinerarioDTO = ItinerarioDTO()

        return dto
    
    def externo_a_dto(self, externo: dict) -> ReservaDTO:
        reserva_dto = ReservaDTO()

        itinerarios: list[ItinerarioDTO] = list()
        for itin in externo.get('itinerarios', list()):
            reserva_dto.itinerarios.append(self._procesar_itinerario(itin))

        return reserva_dto

    def dto_a_externo(self, dto: ReservaDTO) -> dict:
        return dto.__dict__

