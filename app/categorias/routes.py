from flask import Blueprint

bp = Blueprint('categorias', __name__)

@bp.route('/categorias')
def list_categorias():
    return "Listado de categorías"  # Cambia esto por tu lógica real