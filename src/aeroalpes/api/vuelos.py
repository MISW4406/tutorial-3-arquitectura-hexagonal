import aeroalpes.seedwork.presentacion.api as api
from aeroalpes.modulos.vuelos.aplicacion.servicios import ServicioReserva
from aeroalpes.modulos.vuelos.aplicacion.dto import ReservaDTO

from flask import redirect, render_template, request, session, url_for
from aeroalpes.modulos.vuelos.aplicacion.mapeadores import MapeadorReservaDTOJson

bp = api.crear_blueprint('vuelos', '/vuelos')

# a simple page that says hello
@bp.route('/reserva', methods=('POST',))
def reservar():
    reserva_dict = request.json

    map_reserva = MapeadorReservaDTOJson()
    reserva_dto = map_reserva.externo_a_dto(reserva_dict)

    sr = ServicioReserva()
    dto_final = sr.crear_reserva(reserva_dto)
    
    return map_reserva.dto_a_externo(dto_final)

@bp.route('/reserva', methods=('GET',))
@bp.route('/reserva/<id>', methods=('GET',))
def dar_reserva(id=None):
    if id:
        sr = ServicioReserva()
        
        return sr.obtener_reserva_por_id(id)
    else:
        return [{'message': 'GET!'}]