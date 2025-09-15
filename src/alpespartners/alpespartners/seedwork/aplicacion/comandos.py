from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class Comando:
    id: str
    
    def __init__(self):
        self.id = str(uuid4())

class ComandoHandler(ABC):
    @abstractmethod
    def handle(self, comando: Comando):
        raise NotImplementedError

class ExecutorComando:
    def __init__(self, handler: ComandoHandler):
        self.handler = handler
    
    def ejecutar(self, comando: Comando):
        return self.handler.handle(comando)
