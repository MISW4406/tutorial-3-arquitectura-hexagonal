from typing import Dict, Type, List
from .....seedwork.dominio.eventos import EventoDominio, Handler
from ..eventos import ClickRegistrado, ConversionRegistrada, AtribucionAsignada
from .click_handlers import ClickEventHandler
from .conversion_handlers import ConversionEventHandler
from .atribucion_handlers import AtribucionEventHandler

# Registro de handlers por tipo de evento
handlers: Dict[Type[EventoDominio], List[Type[Handler]]] = {
    ClickRegistrado: [],
    ConversionRegistrada: [ClickEventHandler, ConversionEventHandler],
    AtribucionAsignada: [AtribucionEventHandler]
}
