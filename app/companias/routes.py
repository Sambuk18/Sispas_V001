# app/companias/routes.py
from flask import Blueprint
from flask_login import login_required, current_user

bp = Blueprint('companias', __name__)

@bp.route('/')
@login_required
def list_companias():
    return "Listado de compañías"