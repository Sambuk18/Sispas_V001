from flask import Blueprint

bp = Blueprint('pagos', __name__)

@bp.route('/pagos')
def list_pagos():
    return "Listado de pagos"  # Cambia esto por tu lógica real