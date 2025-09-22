from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from ....seedwork.dominio.eventos import EventoDominio

@dataclass
class ClickRegistrado(EventoDominio):
    id_click: str
    id_partner: str
    id_campana: str
    url_origen: str
    url_destino: str
    metadata_cliente: Dict
    timestamp: datetime
    
    def __init__(self, id_click: str, id_partner: str, id_campana: str, 
                 url_origen: str, url_destino: str, metadata_cliente: Dict, timestamp: datetime):
        super().__init__()
        self.id_click = id_click
        self.id_partner = id_partner
        self.id_campana = id_campana
        self.url_origen = url_origen
        self.url_destino = url_destino
        self.metadata_cliente = metadata_cliente
        self.timestamp = timestamp

@dataclass
class ConversionRegistrada(EventoDominio):
    id_conversion: str
    id_click: Optional[str]
    id_partner: str
    id_campana: str
    tipo_conversion: str
    valor: float
    comision: float
    timestamp: datetime
    metadata_cliente: Dict
    
    def __init__(self, id_conversion: str, id_click: Optional[str], id_partner: str, 
                 id_campana: str, tipo_conversion: str, valor: float, comision: float, 
                 timestamp: datetime, metadata_cliente: Dict):
        super().__init__()
        self.id_conversion = id_conversion
        self.id_click = id_click
        self.id_partner = id_partner
        self.id_campana = id_campana
        self.tipo_conversion = tipo_conversion
        self.valor = valor
        self.comision = comision
        self.timestamp = timestamp
        self.metadata_cliente = metadata_cliente

@dataclass
class AtribucionAsignada(EventoDominio):
    id_atribucion: str
    id_conversion: str
    id_partner: str
    id_campana: str
    modelo_atribucion: str
    porcentaje_atribucion: float
    timestamp: datetime
    
    def __init__(self, id_atribucion: str, id_conversion: str, id_partner: str, 
                 id_campana: str, modelo_atribucion: str, porcentaje_atribucion: float, 
                 timestamp: datetime):
        super().__init__()
        self.id_atribucion = id_atribucion
        self.id_conversion = id_conversion
        self.id_partner = id_partner
        self.id_campana = id_campana
        self.modelo_atribucion = modelo_atribucion
        self.porcentaje_atribucion = porcentaje_atribucion
        self.timestamp = timestamp