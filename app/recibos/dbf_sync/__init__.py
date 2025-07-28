from flask import Blueprint

dbf_sync_bp = Blueprint(
    'dbf_sync', __name__,
    template_folder='templates',
    url_prefix='/dbf_sync'  # esto hace que la ruta final sea /dbf_sync/sincronizar
)

from . import routes
