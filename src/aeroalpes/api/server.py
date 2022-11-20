from flask import Flask
from aeroalpes.ejemplos.servicio_busqueda import buscar_itinerarios
from aeroalpes.ejemplos.servicios import ServicioBusqueda
from aeroalpes.modulos.vuelos.dominio.objetos_valor import Odo, Segmento, Leg, ParametroBusca, TipoPasajero, Clase, CodigoIATA
from aeroalpes.modulos.vuelos.dominio.entidades import Aeropuerto, Pasajero

app = Flask(__name__)

@app.route("/")
def hello_world():
    segmentos = [Segmento(legs=[Leg(destino=Aeropuerto(codigo=CodigoIATA(codigo="JFK"), nombre="JFK International Airport"), origen=Aeropuerto(codigo=CodigoIATA(codigo="CPT"), nombre="Cape Town International"))])]
    rutas = [Odo(segmentos=segmentos)]
    #itinerarios = buscar_itinerarios(ruta, ParametroBusca(pasajeros=list()))
    pasajero = Pasajero(tipo=TipoPasajero.ADULTO, clase=Clase.ECONOMICA)
    itinerarios = ServicioBusqueda().buscar_itinerarios(rutas, ParametroBusca(pasajeros=[pasajero]))
    print(itinerarios)
    return f"<h1>Itinerarios</h1><l>{itinerarios}</l>"