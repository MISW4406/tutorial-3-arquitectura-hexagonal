from typing import Dict, List
from .....seedwork.dominio.eventos import Handler
from ..eventos import ConversionRegistrada
from ..repositorios import RepositorioClicks

class ClickEventHandler(Handler):
    def __init__(self, repositorio_clicks: RepositorioClicks):
        self.repositorio_clicks = repositorio_clicks
        
    def handle(self, evento: ConversionRegistrada):
        if evento.id_click:
            click = self.repositorio_clicks.obtener_por_id(evento.id_click)
            if click:
                click.registrar_conversion(evento.valor, evento.comision)
                self.repositorio_clicks.actualizar(click)
