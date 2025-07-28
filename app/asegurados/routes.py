from flask import Blueprint

bp = Blueprint('asegurados', __name__)

@bp.route('/asegurados')
def list_asegurados():
    return "Listado de asegurados"  # Cambia esto por tu lógica real