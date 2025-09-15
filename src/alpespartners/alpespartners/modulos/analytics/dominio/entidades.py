from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from uuid import uuid4

@dataclass
class Entidad:
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class MetricaCampana(Entidad):
    id_campana: str = field()
    id_partner: str = field()
    total_clicks: int = field(default=0)
    total_conversiones: int = field(default=0)
    valor_total_conversiones: float = field(default=0.0)
    comision_total: float = field(default=0.0)
    ultima_actualizacion: datetime = field(default_factory=datetime.now)
    
    def registrar_click(self):
        self.total_clicks += 1
        self.ultima_actualizacion = datetime.now()
    
    def registrar_conversion(self, valor: float, comision: float):
        self.total_conversiones += 1
        self.valor_total_conversiones += valor
        self.comision_total += comision
        self.ultima_actualizacion = datetime.now()
    
    @property
    def tasa_conversion(self) -> float:
        return (self.total_conversiones / self.total_clicks) * 100 if self.total_clicks > 0 else 0
    
    @property
    def valor_promedio_conversion(self) -> float:
        return self.valor_total_conversiones / self.total_conversiones if self.total_conversiones > 0 else 0

@dataclass
class MetricaPartner(Entidad):
    id_partner: str = field()
    metricas_campanas: Dict[str, MetricaCampana] = field(default_factory=dict)
    ultima_actualizacion: datetime = field(default_factory=datetime.now)
    
    def obtener_o_crear_metrica_campana(self, id_campana: str) -> MetricaCampana:
        if id_campana not in self.metricas_campanas:
            self.metricas_campanas[id_campana] = MetricaCampana(
                id_campana=id_campana,
                id_partner=self.id_partner
            )
        return self.metricas_campanas[id_campana]
    
    @property
    def total_clicks(self) -> int:
        return sum(m.total_clicks for m in self.metricas_campanas.values())
    
    @property
    def total_conversiones(self) -> int:
        return sum(m.total_conversiones for m in self.metricas_campanas.values())
    
    @property
    def valor_total_conversiones(self) -> float:
        return sum(m.valor_total_conversiones for m in self.metricas_campanas.values())
    
    @property
    def comision_total(self) -> float:
        return sum(m.comision_total for m in self.metricas_campanas.values())
    
    @property
    def tasa_conversion_global(self) -> float:
        return (self.total_conversiones / self.total_clicks) * 100 if self.total_clicks > 0 else 0
