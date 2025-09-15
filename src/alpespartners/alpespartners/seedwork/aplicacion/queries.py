from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class Query:
    id: str
    
    def __init__(self):
        self.id = str(uuid4())

class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query):
        raise NotImplementedError

class ExecutorQuery:
    def __init__(self, handler: QueryHandler):
        self.handler = handler
    
    def ejecutar(self, query: Query):
        return self.handler.handle(query)
