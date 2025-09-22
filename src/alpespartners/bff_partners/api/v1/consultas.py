import strawberry
import typing
import requests
import os
from .esquemas import *

@strawberry.type
class Query:
    """Consultas GraphQL para Alpes Partners"""
    
    # Consultas de Tracking
    clicks: typing.List[Click] = strawberry.field(resolver=obtener_clicks_partner)
    conversiones: typing.List[Conversion] = strawberry.field(resolver=obtener_conversiones_partner)
    
    # Consultas de Afiliados
    afiliados: typing.List[Afiliado] = strawberry.field(resolver=obtener_afiliados)
    
    # Consultas de Pagos
    pagos: typing.List[Pago] = strawberry.field(resolver=obtener_pagos_partner)
    