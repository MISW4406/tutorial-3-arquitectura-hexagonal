""" Mapeadores para la capa de infrastructura del dominio de vuelos

En este archivo usted encontrará los diferentes mapeadores
encargados de la transformación entre formatos de dominio y DTOs

"""

from aeroalpes.seedwork.dominio.repositorios import Mapeador
from aeroalpes.modulos.vuelos.dominio.objetos_valor import NombreAero, Odo, Leg, Segmento, Itinerario, CodigoIATA
from aeroalpes.modulos.vuelos.dominio.entidades import Proveedor, Aeropuerto, Reserva
from .dto import Reserva as ReservaDTO
from .dto import Itinerario as ItinerarioDTO

class MapeadorReserva(Mapeador):
    _FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'

    def _procesar_itinerario_dto(self, itinerarios_dto: list) -> list[Itinerario]:
        itin_dict = dict()
        
        for itin in itinerarios_dto:
            destino = Aeropuerto(codigo=itin.destino_codigo, nombre=None)
            origen = Aeropuerto(codigo=itin.origen_codigo, nombre=None)
            fecha_salida = itin.fecha_salida
            fecha_llegada = itin.fecha_llegada

            itin_dict.setdefault(str(itin.odo_orden),{}).setdefault(str(itin.segmento_orden), {}).setdefault(str(itin.leg_orden), Leg(fecha_salida, fecha_llegada, origen, destino))

        odos = list()
        for k, odos_dict in itin_dict.items():
            segmentos = list()
            for k, seg_dict in odos_dict.items():
                legs = list()
                for k, leg in seg_dict.items():
                    legs.append(leg)
                segmentos.append(Segmento(legs))
            odos.append(Odo(segmentos))

        return [Itinerario(odos)]

    def _procesar_itinerario(self, itinerario: any) -> list[ItinerarioDTO]:
        itinerarios_dto = list()

        for i, odo in enumerate(itinerario.odos):
            for j, seg in enumerate(odo.segmentos):
                for k, leg in enumerate(seg.legs):
                    itinerario_dto = ItinerarioDTO()
                    itinerario_dto.destino_codigo = leg.destino.codigo
                    itinerario_dto.origen_codigo = leg.origen.codigo
                    itinerario_dto.fecha_salida = leg.fecha_salida
                    itinerario_dto.fecha_llegada = leg.fecha_llegada
                    itinerario_dto.leg_orden = k
                    itinerario_dto.segmento_orden = j
                    itinerario_dto.odo_orden = i

                    itinerarios_dto.append(itinerario_dto)

        return itinerarios_dto

    def obtener_tipo(self) -> type:
        return Reserva.__class__

    def entidad_a_dto(self, entidad: Reserva) -> ReservaDTO:
        
        reserva_dto = ReservaDTO()
        reserva_dto.fecha_creacion = entidad.fecha_creacion
        reserva_dto.fecha_actualizacion = entidad.fecha_actualizacion
        reserva_dto.id = str(entidad.id)

        itinerarios_dto = list()
        
        for itinerario in entidad.itinerarios:
            itinerarios_dto.extend(self._procesar_itinerario(itinerario))

        reserva_dto.itinerarios = itinerarios_dto

        return reserva_dto

    def dto_a_entidad(self, dto: ReservaDTO) -> Reserva:
        reserva = Reserva(dto.id, dto.fecha_creacion, dto.fecha_actualizacion)
        reserva.itinerarios = list()

        itinerarios_dto: list[ItinerarioDTO] = dto.itinerarios

        reserva.itinerarios.extend(self._procesar_itinerario_dto(itinerarios_dto))
        
        return reserva