from flask import Blueprint

bp = Blueprint('taller', __name__)

@bp.route('/taller')
def list_taller():
    return "Listado de taller"  # Cambia esto por tu lógica real