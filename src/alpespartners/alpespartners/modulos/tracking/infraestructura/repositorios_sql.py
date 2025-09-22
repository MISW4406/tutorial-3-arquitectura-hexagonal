from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from ..dominio.entidades import Click, Conversion
from ..dominio.repositorios import RepositorioClicks, RepositorioConversiones
from .modelos import ClickModel, ConversionModel, AtribucionModel

class RepositorioClicksSQL(RepositorioClicks):
    def __init__(self, db: Session):
        self.db = db

    def agregar(self, click: Click):
        db_click = ClickModel(
            id=click.id_click,
            id_partner=click.id_partner,
            id_campana=click.id_campana,
            url_origen=click.url_origen,
            url_destino=click.url_destino,
            timestamp=click.timestamp,
            metadata_cliente=click.metadata_cliente.__dict__,
            total_conversiones=click.total_conversiones,
            valor_total=click.valor_total,
            comision_total=click.comision_total
        )
        self.db.add(db_click)
        self.db.commit()
        self.db.refresh(db_click)

    def obtener_por_id(self, id_click: str) -> Optional[Click]:
        db_click = self.db.query(ClickModel).filter(ClickModel.id == id_click).first()
        if not db_click:
            return None
        return Click(
            id=db_click.id,
            id_partner=db_click.id_partner,
            id_campana=db_click.id_campana,
            url_origen=db_click.url_origen,
            url_destino=db_click.url_destino,
            timestamp=db_click.timestamp,
            metadata_cliente=db_click.metadata_cliente,
            total_conversiones=db_click.total_conversiones,
            valor_total=db_click.valor_total,
            comision_total=db_click.comision_total
        )

    def obtener_por_partner(self, id_partner: str, desde: datetime = None, hasta: datetime = None) -> List[Click]:
        query = self.db.query(ClickModel).filter(ClickModel.id_partner == id_partner)
        if desde:
            query = query.filter(ClickModel.timestamp >= desde)
        if hasta:
            query = query.filter(ClickModel.timestamp <= hasta)
        
        return [
            Click(
                id=db_click.id,
                id_partner=db_click.id_partner,
                id_campana=db_click.id_campana,
                url_origen=db_click.url_origen,
                url_destino=db_click.url_destino,
                timestamp=db_click.timestamp,
                metadata_cliente=db_click.metadata_cliente,
            total_conversiones=db_click.total_conversiones,
            valor_total=db_click.valor_total,
            comision_total=db_click.comision_total
            )
            for db_click in query.all()
        ]
        
    def actualizar(self, click: Click):
        db_click = self.db.query(ClickModel).filter(ClickModel.id == click.id_click).first()
        if db_click:
            db_click.total_conversiones = click.total_conversiones
            db_click.valor_total = click.valor_total
            db_click.comision_total = click.comision_total
            self.db.commit()
            self.db.refresh(db_click)
    
    def obtener_todos(self) -> List[Click]:
        db_clicks = self.db.query(ClickModel).all()
        return [
            Click(
                id=db_click.id,
                id_partner=db_click.id_partner,
                id_campana=db_click.id_campana,
                url_origen=db_click.url_origen,
                url_destino=db_click.url_destino,
                timestamp=db_click.timestamp,
                metadata_cliente=db_click.metadata_cliente,
                total_conversiones=db_click.total_conversiones,
                valor_total=db_click.valor_total,
                comision_total=db_click.comision_total
            )
            for db_click in db_clicks
        ]

class RepositorioConversionesSQL(RepositorioConversiones):
    def __init__(self, db: Session):
        self.db = db

    def agregar(self, conversion: Conversion):
        db_conversion = ConversionModel(
            id=conversion.id,
            id_click=conversion.id_click,
            id_partner=conversion.id_partner,
            id_campana=conversion.id_campana,
            tipo=conversion.tipo.value,
            timestamp=conversion.timestamp,
            metadata_cliente=conversion.metadata_cliente.__dict__,
            valor=conversion.informacion_monetaria.valor,
            moneda=conversion.informacion_monetaria.moneda,
            comision=conversion.informacion_monetaria.comision,
            porcentaje_comision=conversion.informacion_monetaria.porcentaje_comision
        )
        self.db.add(db_conversion)
        self.db.commit()
        self.db.refresh(db_conversion)

    def obtener_por_id(self, id_conversion: str) -> Optional[Conversion]:
        db_conversion = self.db.query(ConversionModel).filter(ConversionModel.id == id_conversion).first()
        if not db_conversion:
            return None
        return self._map_to_domain(db_conversion)

    def obtener_por_partner(self, id_partner: str, desde: datetime = None, hasta: datetime = None) -> List[Conversion]:
        query = self.db.query(ConversionModel).filter(ConversionModel.id_partner == id_partner)
        if desde:
            query = query.filter(ConversionModel.timestamp >= desde)
        if hasta:
            query = query.filter(ConversionModel.timestamp <= hasta)
        
        return [self._map_to_domain(db_conversion) for db_conversion in query.all()]

    def obtener_por_click(self, id_click: str) -> List[Conversion]:
        query = self.db.query(ConversionModel).filter(ConversionModel.id_click == id_click)
        return [self._map_to_domain(db_conversion) for db_conversion in query.all()]

    def actualizar(self, conversion: Conversion):
        db_conversion = self.db.query(ConversionModel).filter(ConversionModel.id == conversion.id).first()
        if db_conversion:
            # Update existing atribuciones
            for atribucion in conversion.atribuciones:
                db_atribucion = AtribucionModel(
                    id=str(uuid4()),
                    id_conversion=conversion.id,
                    modelo=atribucion.modelo.value,
                    porcentaje=atribucion.porcentaje,
                    timestamp=atribucion.timestamp,
                    ventana_atribucion=atribucion.ventana_atribucion
                )
                self.db.add(db_atribucion)
            
            self.db.commit()

    def _map_to_domain(self, db_conversion: ConversionModel) -> Conversion:
        from ..dominio.objetos_valor import TipoConversion, InformacionMonetaria, MetadataCliente, DatosAtribucion, ModeloAtribucion
        
        info_monetaria = InformacionMonetaria(
            valor=db_conversion.valor,
            moneda=db_conversion.moneda,
            comision=db_conversion.comision,
            porcentaje_comision=db_conversion.porcentaje_comision
        )
        
        atribuciones = [
            DatosAtribucion(
                modelo=ModeloAtribucion(db_atrib.modelo),
                porcentaje=db_atrib.porcentaje,
                timestamp=db_atrib.timestamp,
                ventana_atribucion=db_atrib.ventana_atribucion
            )
            for db_atrib in db_conversion.atribuciones
        ]
        
        conversion = Conversion(
            id=db_conversion.id,
            id_click=db_conversion.id_click,
            id_partner=db_conversion.id_partner,
            id_campana=db_conversion.id_campana,
            tipo=TipoConversion(db_conversion.tipo),
            timestamp=db_conversion.timestamp,
            metadata_cliente=MetadataCliente(**db_conversion.metadata_cliente),
            informacion_monetaria=info_monetaria
        )
        conversion.atribuciones = atribuciones
        return conversion
    
    def obtener_todos(self) -> List[Conversion]:
        db_conversions = self.db.query(ConversionModel).all()
        return [self._map_to_domain(db_conversion) for db_conversion in db_conversions]
