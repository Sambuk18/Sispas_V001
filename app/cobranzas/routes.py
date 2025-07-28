from flask import Blueprint

bp = Blueprint('cobranzas', __name__)

@bp.route('/cobranzas')
def list_cobranzas():
    return "Listado de cobranzas"  # Cambia esto por tu lógica real