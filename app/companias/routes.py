# app/companias/routes.py
from flask import Blueprint

bp = Blueprint('companias', __name__)

@bp.route('/')
def list_companias():
    return "Listado de compañías"