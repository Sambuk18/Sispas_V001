from flask import Blueprint

bp = Blueprint('clientes', __name__)

@bp.route('/clientes')
def list_clientes():
    return "Listado de clientes"  # Cambia esto por tu lógica real