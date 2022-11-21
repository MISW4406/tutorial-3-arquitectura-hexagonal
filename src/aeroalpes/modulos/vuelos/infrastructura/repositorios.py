from aeroalpes.seedwork.dominio.repositorios import Repositorio
from aeroalpes.modulos.vuelos.dominio.objetos_valor import NombreAero, Odo, Leg, Segmento, Itinerario, CodigoIATA
from aeroalpes.modulos.vuelos.dominio.entidades import Proveedor, Aeropuerto, Reserva
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

    def obtener_todos(self, id: UUID) -> list[Reserva]:
        ...

    def agregar(self, entity: Reserva):
        ...

    def actualizar(self, entity: Reserva):
        ...

    def eliminar(self, entity_id: UUID):
        ...