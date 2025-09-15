from dataclasses import dataclass
from typing import Dict, Optional

from ....seedwork.aplicacion.comandos import Comando, ComandoHandler
from ..dominio.objetos_valor import MetadataCliente, InformacionMonetaria, TipoConversion, ModeloAtribucion
from .servicios import ServicioTracking

@dataclass
class ComandoRegistrarClick(Comando):
    id_partner: str
    id_campana: str
    url_origen: str
    url_destino: str
    metadata_cliente: Dict
    
    def __init__(self, id_partner: str, id_campana: str, url_origen: str, url_destino: str, metadata_cliente: Dict):
        super().__init__()
        self.id_partner = id_partner
        self.id_campana = id_campana
        self.url_origen = url_origen
        self.url_destino = url_destino
        self.metadata_cliente = metadata_cliente

@dataclass
class ComandoRegistrarConversion(Comando):
    id_partner: str
    id_campana: str
    tipo_conversion: str
    informacion_monetaria: Dict
    metadata_cliente: Dict
    id_click: Optional[str] = None
    
    def __init__(self, id_partner: str, id_campana: str, tipo_conversion: str, 
                 informacion_monetaria: Dict, metadata_cliente: Dict, id_click: Optional[str] = None):
        super().__init__()
        self.id_partner = id_partner
        self.id_campana = id_campana
        self.tipo_conversion = tipo_conversion
        self.informacion_monetaria = informacion_monetaria
        self.metadata_cliente = metadata_cliente
        self.id_click = id_click

@dataclass
class ComandoAsignarAtribucion(Comando):
    id_conversion: str
    modelo: str
    porcentaje: float
    ventana_atribucion: int
    
    def __init__(self, id_conversion: str, modelo: str, porcentaje: float, ventana_atribucion: int):
        super().__init__()
        self.id_conversion = id_conversion
        self.modelo = modelo
        self.porcentaje = porcentaje
        self.ventana_atribucion = ventana_atribucion

class RegistrarClickHandler(ComandoHandler):
    def __init__(self, servicio: ServicioTracking):
        self.servicio = servicio
    
    def handle(self, comando: ComandoRegistrarClick):
        metadata = MetadataCliente(**comando.metadata_cliente)
        return self.servicio.registrar_click(
            id_partner=comando.id_partner,
            id_campana=comando.id_campana,
            url_origen=comando.url_origen,
            url_destino=comando.url_destino,
            metadata_cliente=metadata
        )

class RegistrarConversionHandler(ComandoHandler):
    def __init__(self, servicio: ServicioTracking):
        self.servicio = servicio
    
    def handle(self, comando: ComandoRegistrarConversion):
        tipo = TipoConversion(comando.tipo_conversion)
        info_monetaria = InformacionMonetaria(**comando.informacion_monetaria)
        metadata = MetadataCliente(**comando.metadata_cliente)
        
        return self.servicio.registrar_conversion(
            id_partner=comando.id_partner,
            id_campana=comando.id_campana,
            tipo=tipo,
            informacion_monetaria=info_monetaria,
            metadata_cliente=metadata,
            id_click=comando.id_click
        )

class AsignarAtribucionHandler(ComandoHandler):
    def __init__(self, servicio: ServicioTracking):
        self.servicio = servicio
    
    def handle(self, comando: ComandoAsignarAtribucion):
        modelo_atribucion = ModeloAtribucion(comando.modelo)
        self.servicio.asignar_atribucion(
            id_conversion=comando.id_conversion,
            modelo=modelo_atribucion,
            porcentaje=comando.porcentaje,
            ventana_atribucion=comando.ventana_atribucion
        )
