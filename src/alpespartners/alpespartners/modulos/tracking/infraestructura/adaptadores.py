from datetime import datetime
from typing import Dict, List, Optional

from ..dominio.puertos import (
    IPuertoRegistrarClick,
    IPuertoRegistrarConversion,
    IPuertoAsignarAtribucion,
    IPuertoConsultarConversiones
)
from ..dominio.objetos_valor import MetadataCliente, InformacionMonetaria, TipoConversion, ModeloAtribucion
from ..aplicacion.servicios import ServicioTracking
from .repositorios_sql import RepositorioClicksSQL, RepositorioConversionesSQL
from ..dominio.repositorios import RepositorioClicks, RepositorioConversiones
from .despachadores import DespachadorEventosKafka
from ..aplicacion.comandos import (
    ComandoRegistrarClick, ComandoRegistrarConversion, ComandoAsignarAtribucion,
    RegistrarClickHandler, RegistrarConversionHandler, AsignarAtribucionHandler
)
from ..aplicacion.queries import QueryConversionesPartner, ConversionesPartnerHandler
from ....seedwork.aplicacion.comandos import ExecutorComando
from ....seedwork.aplicacion.queries import ExecutorQuery

class AdaptadorTrackingSQL:
    """Adaptador base que comparte la conexión a la base de datos"""
    def __init__(self, db, producer=None):
        self.db = db
        self.servicio = ServicioTracking(
            repositorio_clicks=RepositorioClicksSQL(db),
            repositorio_conversiones=RepositorioConversionesSQL(db),
            despachador=DespachadorEventosKafka(producer) if producer else None
        )

class AdaptadorRegistrarClickSQL(AdaptadorTrackingSQL, IPuertoRegistrarClick):
    def ejecutar(self,
                id_partner: str,
                id_campana: str,
                url_origen: str,
                url_destino: str,
                metadata_cliente: Dict) -> str:
        comando = ComandoRegistrarClick(
            id_partner=id_partner,
            id_campana=id_campana,
            url_origen=url_origen,
            url_destino=url_destino,
            metadata_cliente=metadata_cliente
        )
        handler = RegistrarClickHandler(self.servicio)
        ejecutor = ExecutorComando(handler)
        return ejecutor.ejecutar(comando)

class AdaptadorRegistrarConversionSQL(AdaptadorTrackingSQL, IPuertoRegistrarConversion):
    def ejecutar(self,
                id_partner: str,
                id_campana: str,
                tipo_conversion: str,
                informacion_monetaria: Dict,
                metadata_cliente: Dict,
                id_click: Optional[str] = None) -> str:
        comando = ComandoRegistrarConversion(
            id_partner=id_partner,
            id_campana=id_campana,
            tipo_conversion=tipo_conversion,
            informacion_monetaria=informacion_monetaria,
            metadata_cliente=metadata_cliente,
            id_click=id_click
        )
        handler = RegistrarConversionHandler(self.servicio)
        ejecutor = ExecutorComando(handler)
        return ejecutor.ejecutar(comando)

class AdaptadorAsignarAtribucionSQL(AdaptadorTrackingSQL, IPuertoAsignarAtribucion):
    def ejecutar(self,
                id_conversion: str,
                modelo: str,
                porcentaje: float,
                ventana_atribucion: int) -> None:
        comando = ComandoAsignarAtribucion(
            id_conversion=id_conversion,
            modelo=modelo,
            porcentaje=porcentaje,
            ventana_atribucion=ventana_atribucion
        )
        handler = AsignarAtribucionHandler(self.servicio)
        ejecutor = ExecutorComando(handler)
        ejecutor.ejecutar(comando)

class AdaptadorConsultarConversionesSQL(AdaptadorTrackingSQL, IPuertoConsultarConversiones):
    def ejecutar(self,
                id_partner: str,
                desde: Optional[datetime] = None,
                hasta: Optional[datetime] = None) -> List[Dict]:
        query = QueryConversionesPartner(
            id_partner=id_partner,
            desde=desde,
            hasta=hasta
        )
        handler = ConversionesPartnerHandler(self.servicio)
        ejecutor = ExecutorQuery(handler)
        conversiones = ejecutor.ejecutar(query)
        return [conversion.__dict__ for conversion in conversiones]
