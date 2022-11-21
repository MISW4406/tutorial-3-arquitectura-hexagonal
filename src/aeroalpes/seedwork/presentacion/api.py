import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

def crear_blueprint(identificador: str, prefijo_url: str):
    return Blueprint(identificador, __name__, url_prefix=prefijo_url)