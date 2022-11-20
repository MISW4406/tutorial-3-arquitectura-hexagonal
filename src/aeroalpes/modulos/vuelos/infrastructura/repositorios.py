from aeroalpes.seedwork.dominio.repositorios import Repositorio
from aeroalpes.modulos.vuelos.dominio.objetos_valor import CodigoIATA
from aeroalpes.modulos.vuelos.dominio.objetos_valor import NombreAero, Odo, Leg, Segmento
from .objetos_valor import Itinerario
from .entidades import Proveedor, Aeropuerto, Reserva
from uuid import UUID

class RepositorioProveedores(Repositorio):
    @staticmethod
    def obtener_todos() -> list[Proveedor]:

        origen=Aeropuerto(codigo="CPT", nombre="Cape Town International")
        destino=Aeropuerto(codigo="JFK", nombre="JFK International Airport")
        legs=[Leg(origen=origen, destino=destino)]
        segmentos = [Segmento(legs)]
        odos=[Odo(segmentos=segmentos)]

        proveedor = Proveedor(codigo=CodigoIATA(codigo="AV"), nombre=NombreAero(nombre= "Avianca"))
        proveedor.itinerarios = [Itinerario(odos=odos, proveedor=proveedor)]
        return [proveedor]


class SqlLiteMapper:
    pass

class RepositorioReservas(Repositorio):
    def obtener_por_id(self, id: UUID) -> Reserva:
        ...