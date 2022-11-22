from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = None

def init_db(app: Flask):
    global db 
    db = SQLAlchemy(app)