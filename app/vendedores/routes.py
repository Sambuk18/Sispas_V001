from flask import Blueprint

bp = Blueprint('vendedores', __name__)

@bp.route('/vendedores')
def list_vendedores():
    return "Listado de vendedores"  # Cambia esto por tu lógica real