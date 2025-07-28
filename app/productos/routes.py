from flask import Blueprint

bp = Blueprint('productos', __name__)

@bp.route('/productos')
def list_productos():
    return "Listado de productos"  # Implementa tu lógica real aquí