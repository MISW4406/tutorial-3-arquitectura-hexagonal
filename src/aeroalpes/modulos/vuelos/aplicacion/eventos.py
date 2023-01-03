from __future__ import annotations
from dataclasses import dataclass, field
from aeroalpes.seedwork.aplicacion.eventos import (EventoIntegracion)

@dataclass
class ReservaCreada(EventoIntegracion):
    ...