from aeroalpes.seedwork.aplicacion.servicios import Servicio
from aeroalpes.modulos.vuelos.dominio.entidades import Reserva
from aeroalpes.modulos.vuelos.dominio.fabricas import FabricaVuelos
from aeroalpes.modulos.vuelos.infrastructura.fabricas import FabricaRepositorio
from aeroalpes.modulos.vuelos.infrastructura.repositorios import RepositorioReservas
from .mapeadores import MapeadorReserva

from .dto import ReservaDTO

class ServicioReserva(Servicio):

    def crear_reserva(self, reserva_dto: ReservaDTO) -> ReservaDTO():
        fabrica_vuelos = FabricaVuelos()
        reserva: Reserva = fabrica_vuelos.crear_objeto(reserva_dto, MapeadorReserva())

        fabrica_repositorios = FabricaRepositorio()
        repositorio = fabrica_repositorios.crear_objeto(RepositorioReservas.__class__)
        repositorio.agregar(reserva)

        return fabrica_vuelos.crear_objeto(reserva, MapeadorReserva())

