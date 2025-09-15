from datetime import datetime
from typing import List, Optional
from alpespartners.modulos.tracking.dominio.entidades import Click, Conversion
from alpespartners.modulos.tracking.dominio.repositorios import RepositorioClicks, RepositorioConversiones

class RepositorioClicksMemoria(RepositorioClicks):
    def __init__(self):
        self.clicks = {}

    def agregar(self, click: Click):
        self.clicks[click.id] = click

    def obtener_por_id(self, id: str) -> Optional[Click]:
        return self.clicks.get(id)
        
    def obtener_por_partner(self, id_partner: str, desde: datetime = None, hasta: datetime = None) -> List[Click]:
        clicks = []
        for click in self.clicks.values():
            if click.id_partner == id_partner:
                if desde and click.fecha < desde:
                    continue
                if hasta and click.fecha > hasta:
                    continue
                clicks.append(click)
        return clicks

class RepositorioConversionesMemoria(RepositorioConversiones):
    def __init__(self):
        self.conversiones = {}

    def agregar(self, conversion: Conversion):
        self.conversiones[conversion.id] = conversion

    def obtener_por_id(self, id: str) -> Optional[Conversion]:
        return self.conversiones.get(id)

    def obtener_por_partner(self, id_partner: str, desde: Optional[datetime] = None, hasta: Optional[datetime] = None) -> List[Conversion]:
        conversiones = []
        for conversion in self.conversiones.values():
            if conversion.id_partner == id_partner:
                if desde and conversion.fecha < desde:
                    continue
                if hasta and conversion.fecha > hasta:
                    continue
                conversiones.append(conversion)
        return conversiones
        
    def obtener_por_click(self, id_click: str) -> List[Conversion]:
        conversiones = []
        for conversion in self.conversiones.values():
            if conversion.id_click == id_click:
                conversiones.append(conversion)
        return conversiones
        
    def actualizar(self, conversion: Conversion):
        if conversion.id in self.conversiones:
            self.conversiones[conversion.id] = conversion
