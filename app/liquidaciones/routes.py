from flask import Blueprint

bp = Blueprint('liquidaciones', __name__)

@bp.route('/liquidaciones')
def list_liquidaciones():
    return "Listado de liquidaciones"  # Cambia esto por tu lógica real