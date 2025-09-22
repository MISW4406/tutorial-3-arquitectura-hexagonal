from typing import Dict, List
from .....seedwork.dominio.eventos import Handler
from ..eventos import AtribucionAsignada
from ..repositorios import RepositorioConversiones, RepositorioClicks

class AtribucionEventHandler(Handler):
    def __init__(self, repositorio_conversiones: RepositorioConversiones, repositorio_clicks: RepositorioClicks):
        self.repositorio_conversiones = repositorio_conversiones
        self.repositorio_clicks = repositorio_clicks
        
    def handle(self, evento: AtribucionAsignada):
        # Cuando se asigna una atribución, podríamos:
        # 1. Actualizar métricas de la campaña
        # 2. Actualizar comisiones de partners
        # 3. Generar reportes o notificaciones
        conversion = self.repositorio_conversiones.obtener_por_id(evento.id_conversion)
        if conversion and conversion.id_click:
            click = self.repositorio_clicks.obtener_por_id(conversion.id_click)
            if click:
                # Actualizar métricas del click basadas en la atribución
                click.registrar_conversion(
                    valor=conversion.informacion_monetaria.valor * (evento.porcentaje_atribucion / 100),
                    comision=conversion.informacion_monetaria.comision * (evento.porcentaje_atribucion / 100)
                )
                self.repositorio_clicks.actualizar(click)
