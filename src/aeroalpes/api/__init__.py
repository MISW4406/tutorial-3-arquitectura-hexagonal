import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func

# Identifica el directorio base
basedir = os.path.abspath(os.path.dirname(__file__))

db = None

def init_db(app: Flask):
    db = SQLAlchemy(app)


def create_app(configuracion=None):
    # Init la aplicacion de Flask
    app = Flask(__name__, instance_relative_config=True)

    # Configuracion de BD
    app.config['SQLALCHEMY_DATABASE_URI'] =\
            'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Importa Blueprints
    from . import cliente
    from . import hoteles
    from . import pagos
    from . import precios_dinamicos
    from . import vehiculos
    from . import vuelos

    # Registro de Blueprints
    app.register_blueprint(cliente.bp)
    app.register_blueprint(hoteles.bp)
    app.register_blueprint(pagos.bp)
    app.register_blueprint(precios_dinamicos.bp)
    app.register_blueprint(vehiculos.bp)
    app.register_blueprint(vuelos.bp)

    # Inicializa la DB
    init_db(db)

    return app
