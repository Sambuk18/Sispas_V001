from flask import Blueprint

bp = Blueprint('proveedores', __name__)

@bp.route('/proveedores')
def list_proveedores():
    return "Listado de proveedores"  # Cambia esto por tu lógica real