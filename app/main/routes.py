from flask import Blueprint, redirect, url_for, render_template
from flask_login import current_user
from app import db

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
    

@main_bp.route('/keepalive', methods=['POST'])
def keepalive():
    # Actualiza la última actividad para evitar el logout
    session['last_activity'] = time.time()
    return {'status': 'success'}, 200