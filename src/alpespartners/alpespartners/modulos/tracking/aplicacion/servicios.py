from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from ..dominio.entidades import Click, Conversion
from ..dominio.repositorios import RepositorioClicks, RepositorioConversiones
from ..dominio.objetos_valor import MetadataCliente, InformacionMonetaria, DatosAtribucion, TipoConversion, ModeloAtribucion
from ..dominio.eventos import ClickRegistrado, ConversionRegistrada, AtribucionAsignada
from ..dominio.handlers import handlers
from ....seedwork.dominio.eventos import Despachador

@dataclass
class ServicioTracking:
    repositorio_clicks: RepositorioClicks
    repositorio_conversiones: RepositorioConversiones
    despachador: Despachador

    def registrar_click(self, 
                       id_partner: str,
                       id_campana: str,
                       url_origen: str,
                       url_destino: str,
                       metadata_cliente: MetadataCliente) -> str:
        click = Click(
            id_partner=id_partner,
            id_campana=id_campana,
            url_origen=url_origen,
            url_destino=url_destino,
            metadata_cliente=metadata_cliente,
            timestamp=datetime.now()
        )
        self.repositorio_clicks.agregar(click)
        
        evento = ClickRegistrado(
            id_click=click.id_click,
            id_partner=click.id_partner,
            id_campana=click.id_campana,
            url_origen=click.url_origen,
            url_destino=click.url_destino,
            metadata_cliente=click.metadata_cliente.__dict__,
            timestamp=click.timestamp
        )
        self.despachador.publicar_evento(evento)
        
        return click.id_click

    def registrar_conversion(self,
                           id_partner: str,
                           id_campana: str,
                           tipo: TipoConversion,
                           informacion_monetaria: InformacionMonetaria,
                           metadata_cliente: MetadataCliente,
                           id_click: Optional[str] = None) -> str:
        conversion = Conversion(
            id_partner=id_partner,
            id_campana=id_campana,
            id_click=id_click,
            tipo=tipo,
            informacion_monetaria=informacion_monetaria,
            metadata_cliente=metadata_cliente,
            timestamp=datetime.now()
        )
        conversion.registrar_conversion()
        self.repositorio_conversiones.agregar(conversion)
        
        evento = ConversionRegistrada(
            id_conversion=conversion.id_conversion,
            id_click=conversion.id_click,
            id_partner=conversion.id_partner,
            id_campana=conversion.id_campana,
            tipo_conversion=conversion.tipo.value,
            valor=conversion.informacion_monetaria.valor,
            comision=conversion.informacion_monetaria.comision,
            timestamp=conversion.timestamp,
            metadata_cliente=conversion.metadata_cliente.__dict__
        )
        
        for handler_class in handlers.get(type(evento), []):
            if handler_class.__name__ == 'ClickEventHandler':
                handler = handler_class(self.repositorio_clicks)
            elif handler_class.__name__ == 'ConversionEventHandler':
                handler = handler_class(self.repositorio_conversiones)
            elif handler_class.__name__ == 'AtribucionEventHandler':
                handler = handler_class(self.repositorio_conversiones, self.repositorio_clicks)
            handler.handle(evento)
            
        self.despachador.publicar_evento(evento)
        
        return conversion.id_conversion

    def asignar_atribucion(self,
                          id_conversion: str,
                          modelo: ModeloAtribucion,
                          porcentaje: float,
                          ventana_atribucion: int):
        conversion = self.repositorio_conversiones.obtener_por_id(id_conversion)
        datos_atribucion = DatosAtribucion(
            modelo=modelo,
            porcentaje=porcentaje,
            timestamp=datetime.now(),
            ventana_atribucion=ventana_atribucion
        )
        conversion.asignar_atribucion(datos_atribucion)
        self.repositorio_conversiones.actualizar(conversion)
        
        evento = AtribucionAsignada(
            id_atribucion=str(len(conversion.atribuciones)),
            id_conversion=conversion.id_conversion,
            id_partner=conversion.id_partner,
            id_campana=conversion.id_campana,
            modelo_atribucion=modelo.value,
            porcentaje_atribucion=porcentaje,
            timestamp=datos_atribucion.timestamp
        )
        self.despachador.publicar_evento(evento)

    def obtener_clicks_partner(self,
                               id_partner: str,
                               desde: Optional[datetime] = None,
                               hasta: Optional[datetime] = None) -> List[Click]:
        return self.repositorio_clicks.obtener_por_partner(id_partner, desde, hasta)

    def obtener_conversiones_partner(self, 
                                   id_partner: str, 
                                   desde: Optional[datetime] = None, 
                                   hasta: Optional[datetime] = None) -> List[Conversion]:
        return self.repositorio_conversiones.obtener_por_partner(id_partner, desde, hasta)

