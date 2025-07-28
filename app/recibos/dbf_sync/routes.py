from flask import render_template, redirect, url_for, flash
from . import dbf_sync_bp
from .sync_logic import sync_dbf_to_mariadb

@dbf_sync_bp.route('/sincronizar', methods=['POST'])
def sincronizar_datos():
    try:
        resultados = sync_dbf_to_mariadb()
        flash(f"Sincronización finalizada. {resultados['total_inserted']} registros insertados.", "success")
    except Exception as e:
        flash(f"Error durante la sincronización: {str(e)}", "danger")
    return redirect(url_for('recibos.list_recibos'))
