import aeroalpes.seedwork.presentacion.api as api
from aeroalpes.modulos.vuelos.applicacion.servicios import ServicioReserva
from aeroalpes.modulos.vuelos.applicacion.dto import ReservaDTO

from flask import redirect, render_template, request, session, url_for
from aeroalpes.modulos.vuelos.applicacion.mapeadores import MapeadorReservaDTOJson

bp = api.crear_blueprint('vuelos', '/vuelos')

# a simple page that says hello
@bp.route('/reserva', methods=('POST',))
def reservar():
    reserva_dict = request.json

    print(type(reserva_dict))

    map_reserva = MapeadorReservaDTOJson()
    reserva_dto = map_reserva.externo_a_dto(reserva_dict)

    sr = ServicioReserva()
    sr.crear_reserva(reserva_dto)
    
    return reserva_dict

@bp.route('/reserva', methods=('GET',))
def dar_reserva():
    return {'message': 'GET!'}