from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from ....seedwork.aplicacion.queries import Query, QueryHandler
from ..dominio.entidades import Conversion
from .servicios import ServicioTracking

@dataclass
class QueryConversionesPartner(Query):
    id_partner: str
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None

class ConversionesPartnerHandler(QueryHandler):
    def __init__(self, servicio: ServicioTracking):
        self.servicio = servicio
    
    def handle(self, query: QueryConversionesPartner) -> List[Conversion]:
        return self.servicio.obtener_conversiones_partner(
            id_partner=query.id_partner,
            desde=query.desde,
            hasta=query.hasta
        )
