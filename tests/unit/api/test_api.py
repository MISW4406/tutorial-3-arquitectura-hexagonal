import os
import tempfile

import pytest
import json

from aeroalpes.api import create_app, importar_modelos_alchemy
from aeroalpes.config.db import init_db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": db_path})

    # create the database and load test data
    with app.app_context():
        yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


def test_servidor_levanta(client):
    # Dado un cliente a endpoint health
    rv = client.get("/health")

    # Devuelve estados the UP el servidor
    assert rv.data is not None
    assert rv.status_code == 200

    response = json.loads(rv.data)

    assert response["status"] == "up"


@pytest.fixture
def reserva_correcta():
    return {
        "itinerarios": [
            {
                "odos": [
                    {
                        "segmentos": [
                            {
                                "legs": [
                                    {
                                        "fecha_salida": "2022-11-22T13:11:00Z",
                                        "fecha_llegada": "2022-11-22T15:11:00Z",
                                        "destino": {
                                            "codigo": "JFK",
                                            "nombre": "John F. Kennedy International Airport",
                                        },
                                        "origen": {
                                            "codigo": "BOG",
                                            "nombre": "El Dorado - Bogotá International Airport (BOG)",
                                        },
                                    },
                                    {
                                        "fecha_salida": "2022-11-22T16:00:00Z",
                                        "fecha_llegada": "2022-11-22T23:55:00Z",
                                        "destino": {
                                            "codigo": "LAX",
                                            "nombre": "Aeropuerto Internacional de Los Ángeles (Los Angeles International Airport)",
                                        },
                                        "origen": {
                                            "codigo": "JFK",
                                            "nombre": "El Dorado - Bogotá International Airport (BOG)",
                                        },
                                    },
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def reserva_sin_itinerarios():
    return {"itinerarios": []}


@pytest.fixture
def reserva_sin_odos_en_itinerario():
    return {"itinerarios": [{"odos": []}]}


@pytest.fixture
def reserva_sin_segmentos_en_odos():
    return {"itinerarios": [{"odos": [{"segmentos": []}]}]}


@pytest.fixture
def reserva_sin_legs_en_segmentos():
    return {"itinerarios": [{"odos": [{"segmentos": []}]}]}


@pytest.mark.parametrize(
    "input, expected_status",
    [
        ("reserva_sin_itinerarios", 400),
        ("reserva_sin_odos_en_itinerario", 400),
        ("reserva_sin_segmentos_en_odos", 400),
        ("reserva_sin_legs_en_segmentos", 400),
        ("reserva_correcta", 200),
    ],
)
def test_reservar_vuelo(input, expected_status, request, client):
    input = request.getfixturevalue(input)
    rv = client.post(
        "/vuelos/reserva", data=json.dumps(input), content_type="application/json"
    )
    assert rv is not None
