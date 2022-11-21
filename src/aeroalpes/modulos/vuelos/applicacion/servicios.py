from aeroalpes.seedwork.aplicacion.servicios import Servicio
from aeroalpes.modulos.vuelos.dominio.entidades import Reserva
from aeroalpes.modulos.vuelos.dominio.fabricas import FabricaVuelos
from aeroalpes.modulos.vuelos.infrastructura.repositorios import RepositorioReservas
from .mapeadores import MapeadorReserva
from .dto import ReservaDTO

class ServicioReserva(Servicio):

    def crear_reserva(self, reserva_dto: ReservaDTO) -> ReservaDTO():
        fabrica = FabricaVuelos()
        reserva: Reserva = fabrica.crear_objeto(reserva_dto, MapeadorReserva())
        repositorio = RepositorioReservas()
        repositorio.agregar(reserva)

        return fabrica.crear_objeto(reserva, MapeadorReserva())

