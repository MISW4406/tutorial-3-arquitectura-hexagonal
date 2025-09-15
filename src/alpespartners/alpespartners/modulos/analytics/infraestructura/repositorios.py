from typing import Optional, List, Dict
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Session

from ...analytics.dominio.entidades import MetricaPartner, MetricaCampana
from ...analytics.dominio.repositorios import RepositorioMetricas
from ....config.database import Base

class MetricaPartnerModel(Base):
    __tablename__ = "metricas_partners"
    
    id = Column(String, primary_key=True)
    id_partner = Column(String, index=True)
    metricas_campanas = Column(JSON)  # Stored as JSON for simplicity
    ultima_actualizacion = Column(DateTime)

class RepositorioMetricasSQL(RepositorioMetricas):
    def __init__(self, db: Session):
        self.db = db
    
    def obtener_metricas_partner(self, id_partner: str) -> Optional[MetricaPartner]:
        db_metricas = self.db.query(MetricaPartnerModel).filter(
            MetricaPartnerModel.id_partner == id_partner
        ).first()
        
        if not db_metricas:
            return None
            
        metricas_campanas = {}
        for id_campana, data in db_metricas.metricas_campanas.items():
            metricas_campanas[id_campana] = MetricaCampana(
                id=data.get('id'),
                id_campana=id_campana,
                id_partner=id_partner,
                total_clicks=data.get('total_clicks', 0),
                total_conversiones=data.get('total_conversiones', 0),
                valor_total_conversiones=data.get('valor_total_conversiones', 0.0),
                comision_total=data.get('comision_total', 0.0),
                ultima_actualizacion=data.get('ultima_actualizacion')
            )
        
        return MetricaPartner(
            id=db_metricas.id,
            id_partner=db_metricas.id_partner,
            metricas_campanas=metricas_campanas,
            ultima_actualizacion=db_metricas.ultima_actualizacion
        )
    
    def obtener_metricas_campana(self, id_campana: str) -> Optional[MetricaCampana]:
        # Search through all partners for this campaign
        all_partners = self.db.query(MetricaPartnerModel).all()
        for partner in all_partners:
            if id_campana in partner.metricas_campanas:
                data = partner.metricas_campanas[id_campana]
                return MetricaCampana(
                    id=data.get('id'),
                    id_campana=id_campana,
                    id_partner=partner.id_partner,
                    total_clicks=data.get('total_clicks', 0),
                    total_conversiones=data.get('total_conversiones', 0),
                    valor_total_conversiones=data.get('valor_total_conversiones', 0.0),
                    comision_total=data.get('comision_total', 0.0),
                    ultima_actualizacion=data.get('ultima_actualizacion')
                )
        return None
    
    def guardar_metricas_partner(self, metricas: MetricaPartner) -> None:
        # Convert campaign metrics to JSON-serializable format
        metricas_json = {}
        for id_campana, metrica in metricas.metricas_campanas.items():
            metricas_json[id_campana] = {
                'id': metrica.id,
                'total_clicks': metrica.total_clicks,
                'total_conversiones': metrica.total_conversiones,
                'valor_total_conversiones': metrica.valor_total_conversiones,
                'comision_total': metrica.comision_total,
                'ultima_actualizacion': metrica.ultima_actualizacion.isoformat()
            }
        
        db_metricas = self.db.query(MetricaPartnerModel).filter(
            MetricaPartnerModel.id_partner == metricas.id_partner
        ).first()
        
        if db_metricas:
            db_metricas.metricas_campanas = metricas_json
            db_metricas.ultima_actualizacion = metricas.ultima_actualizacion
        else:
            db_metricas = MetricaPartnerModel(
                id=metricas.id,
                id_partner=metricas.id_partner,
                metricas_campanas=metricas_json,
                ultima_actualizacion=metricas.ultima_actualizacion
            )
            self.db.add(db_metricas)
        
        self.db.commit()
    
    def obtener_todas_metricas(self) -> List[MetricaPartner]:
        db_metricas = self.db.query(MetricaPartnerModel).all()
        return [self.obtener_metricas_partner(m.id_partner) for m in db_metricas]
