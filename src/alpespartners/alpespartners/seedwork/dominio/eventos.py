from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from uuid import uuid4

@dataclass
class EventoDominio:
    id: str
    fecha: datetime
    
    def __init__(self):
        self.id = str(uuid4())
        self.fecha = datetime.now()

class Despachador:
    @abstractmethod
    def publicar_evento(self, evento: EventoDominio):
        raise NotImplementedError

class Handler:
    @abstractmethod
    def handle(self, evento: EventoDominio):
        raise NotImplementedError
