from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

from ..dominio.entidades import MetricaPartner, MetricaCampana
from ..dominio.repositorios import RepositorioMetricas

@dataclass
class ServicioAnalytics:
    repositorio: RepositorioMetricas
    
    def procesar_click(self, id_partner: str, id_campana: str) -> None:
        """Procesa un nuevo click registrado"""
        metricas = self.repositorio.obtener_metricas_partner(id_partner)
        if not metricas:
            metricas = MetricaPartner(id_partner=id_partner)
        
        metrica_campana = metricas.obtener_o_crear_metrica_campana(id_campana)
        metrica_campana.registrar_click()
        
        self.repositorio.guardar_metricas_partner(metricas)
    
    def procesar_conversion(
        self,
        id_partner: str,
        id_campana: str,
        valor: float,
        comision: float
    ) -> None:
        """Procesa una nueva conversión registrada"""
        metricas = self.repositorio.obtener_metricas_partner(id_partner)
        if not metricas:
            metricas = MetricaPartner(id_partner=id_partner)
        
        metrica_campana = metricas.obtener_o_crear_metrica_campana(id_campana)
        metrica_campana.registrar_conversion(valor, comision)
        
        self.repositorio.guardar_metricas_partner(metricas)
    
    def obtener_metricas_partner(self, id_partner: str) -> Optional[MetricaPartner]:
        """Obtiene las métricas actuales de un partner"""
        return self.repositorio.obtener_metricas_partner(id_partner)
    
    def obtener_metricas_campana(self, id_campana: str) -> Optional[MetricaCampana]:
        """Obtiene las métricas actuales de una campaña"""
        return self.repositorio.obtener_metricas_campana(id_campana)
