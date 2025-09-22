import typing
import strawberry
import uuid
import requests
import os
from datetime import datetime
from decimal import Decimal

ALPES_PARTNERS_HOST = os.getenv("ALPES_PARTNERS_HOST", "localhost")
ALPES_PARTNERS_PORT = os.getenv("ALPES_PARTNERS_PORT", "8000")
FORMATO_FECHA = '%Y-%m-%dT%H:%M:%S'

def obtener_clicks_partner(partner_id: str = None) -> typing.List["Click"]:
    """Obtiene clicks de un partner específico o todos"""
    url = f'http://{ALPES_PARTNERS_HOST}:{ALPES_PARTNERS_PORT}/v1/tracking/clicks'
    if partner_id:
        url += f"?partner_id={partner_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        clicks_json = response.json()
        clicks = []
        
        for click in clicks_json:
            clicks.append(
                Click(
                    id=click.get('id'),
                    id_partner=click.get('id_partner'),
                    id_campana=click.get('id_campana'),
                    url_origen=click.get('url_origen'),
                    url_destino=click.get('url_destino'),
                    timestamp=datetime.strptime(click.get('timestamp'), FORMATO_FECHA)
                )
            )
        return clicks
    except Exception as e:
        print(f"Error obteniendo clicks: {e}")
        return []

def obtener_conversiones_partner(partner_id: str = None) -> typing.List["Conversion"]:
    """Obtiene conversiones de un partner específico o todas"""
    url = f'http://{ALPES_PARTNERS_HOST}:{ALPES_PARTNERS_PORT}/v1/tracking/conversiones'
    if partner_id:
        url += f"?partner_id={partner_id}"
    
    try:
        response = requests.get(url)
        conversiones_json = response.json()
        conversiones = []
        
        for conversion in conversiones_json:
            conversiones.append(
                Conversion(
                    id=conversion.get('id'),
                    id_partner=conversion.get('id_partner'),
                    id_campana=conversion.get('id_campana'),
                    tipo_conversion=conversion.get('tipo_conversion'),
                    valor=float(conversion.get('valor', 0)),
                    moneda=conversion.get('moneda'),
                    timestamp=datetime.strptime(conversion.get('timestamp'), FORMATO_FECHA)
                )
            )
        return conversiones
    except Exception as e:
        print(f"Error obteniendo conversiones: {e}")
        return []

def obtener_afiliados() -> typing.List["Afiliado"]:
    """Obtiene lista de afiliados"""
    url = f'http://{ALPES_PARTNERS_HOST}:{ALPES_PARTNERS_PORT}/v1/afiliados'
    
    try:
        response = requests.get(url)
        afiliados_json = response.json()
        afiliados = []
        
        for afiliado in afiliados_json:
            afiliados.append(
                Afiliado(
                    id=afiliado.get('id'),
                    codigo_afiliado=afiliado.get('codigo_afiliado'),
                    nombre=afiliado.get('nombre'),
                    email=afiliado.get('email'),
                    tipo_afiliado=afiliado.get('tipo_afiliado'),
                    estado=afiliado.get('estado'),
                    fecha_registro=datetime.strptime(afiliado.get('fecha_registro'), FORMATO_FECHA)
                )
            )
        return afiliados
    except Exception as e:
        print(f"Error obteniendo afiliados: {e}")
        return []

def obtener_pagos_partner(partner_id: str = None) -> typing.List["Pago"]:
    """Obtiene pagos de un partner específico o todos"""
    url = f'http://{ALPES_PARTNERS_HOST}:{ALPES_PARTNERS_PORT}/v1/pagos'
    if partner_id:
        url += f"?partner_id={partner_id}"
    
    try:
        response = requests.get(url)
        pagos_json = response.json()
        pagos = []
        
        for pago in pagos_json:
            pagos.append(
                Pago(
                    id=pago.get('id'),
                    id_partner=pago.get('id_partner'),
                    monto=float(pago.get('monto', 0)),
                    moneda=pago.get('moneda'),
                    estado=pago.get('estado'),
                    tipo_pago=pago.get('tipo_pago'),
                    fecha_creacion=datetime.strptime(pago.get('fecha_creacion'), FORMATO_FECHA)
                )
            )
        return pagos
    except Exception as e:
        print(f"Error obteniendo pagos: {e}")
        return []

@strawberry.type
class Click:
    id: str
    id_partner: str
    id_campana: str
    url_origen: str
    url_destino: str
    timestamp: datetime

@strawberry.type
class Conversion:
    id: str
    id_partner: str
    id_campana: str
    tipo_conversion: str
    valor: float
    moneda: str
    timestamp: datetime

@strawberry.type
class Afiliado:
    id: str
    codigo_afiliado: str
    nombre: str
    email: str
    tipo_afiliado: str
    estado: str
    fecha_registro: datetime

@strawberry.type
class Pago:
    id: str
    id_partner: str
    monto: float
    moneda: str
    estado: str
    tipo_pago: str
    fecha_creacion: datetime

@strawberry.type
class DashboardPartner:
    """Dashboard agregado para partners"""
    partner_id: str
    nombre_partner: str
    total_clicks: int
    total_conversiones: int
    total_comisiones: float
    conversion_rate: float
    ultimo_pago: typing.Optional[datetime]

@strawberry.type
class RespuestaOperacion:
    mensaje: str
    codigo: int
    exito: bool


