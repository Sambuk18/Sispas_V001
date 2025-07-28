from flask import Blueprint

bp = Blueprint('mecanicos', __name__)

@bp.route('/mecanicos')
def list_mecanicos():
    return "Listado de mecanicos"  # Cambia esto por tu lógica real