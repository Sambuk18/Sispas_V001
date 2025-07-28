from flask import Blueprint

bp = Blueprint('gastos', __name__)

@bp.route('/gastos')
def list_gastos():
    return "Listado de gastos"  # Cambia esto por tu lógica real