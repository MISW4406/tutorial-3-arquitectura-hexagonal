from __future__ import annotations
from dataclasses import dataclass, field
from aeroalpes.seedwork.dominio.eventos import (EventoDominio)

@dataclass
class ReservaCreada(EventoDominio):
    ...
    
@dataclass
class ReservaCancelada(EventoDominio):
    ...