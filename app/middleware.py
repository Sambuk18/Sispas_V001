from flask import session, request, redirect, url_for, flash
import time

def setup_session_timeout(app):
    @app.before_request
    def check_session_timeout():
        # Excluir rutas que no requieren sesión
        if request.endpoint in ['auth.login','/', 'static','dashboard']:
            return
        
        if 'last_activity' in session:
            elapsed = time.time() - session['last_activity']
            if elapsed > 3600:  # 1 hora en segundos
                session.clear()
                flash('Tu sesión ha expirado por inactividad', 'warning')
                return redirect(url_for('auth.login'))
        
        session['last_activity'] = time.time()