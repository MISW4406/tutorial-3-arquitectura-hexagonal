from aeroalpes.seedwork.aplicacion.servicios import Servicio
from aeroalpes.modulos.vuelos.dominio.entidades import Reserva
from aeroalpes.modulos.vuelos.dominio.fabricas import FabricaVuelos
from .dto import ReservaDTO

class ServicioReserva(Servicio):

    def crear_reserva(self, reserva_dto: ReservaDTO):
        fabrica = FabricaVuelos()
        fabrica.crear_objeto(obj)
