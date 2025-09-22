from typing import Dict, List
from datetime import datetime
from .....seedwork.dominio.eventos import Handler
from ..eventos import ConversionRegistrada
from ..repositorios import RepositorioConversiones
from ..objetos_valor import DatosAtribucion, ModeloAtribucion

class ConversionEventHandler(Handler):
    def __init__(self, repositorio_conversiones: RepositorioConversiones):
        self.repositorio_conversiones = repositorio_conversiones
        
    def handle(self, evento: ConversionRegistrada):
        conversion = self.repositorio_conversiones.obtener_por_id(evento.id_conversion)
        if conversion:
            if evento.valor > 1000:
                datos_atribucion = DatosAtribucion(
                    modelo=ModeloAtribucion.ULTIMO_CLICK,
                    porcentaje=100.0,
                    timestamp=datetime.now(),
                    ventana_atribucion=30
                )
                conversion.asignar_atribucion(datos_atribucion)
                self.repositorio_conversiones.actualizar(conversion)
