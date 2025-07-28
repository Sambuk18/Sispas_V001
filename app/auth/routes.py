from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.models import User
from app.auth.forms import LoginForm
from app.auth.forms import RegistrationForm

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main_bp.dashboard'))
            else:
                flash('Tu cuenta no está activa. Por favor contacta al administrador.', 'warning')
        else:
            flash('Email o contraseña incorrectos', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Ruta para mostrar el perfil del usuario"""
    return render_template('auth/profile.html', user=current_user)

from .forms import RegistrationForm  # Importación correcta

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    print("Campos del formulario:", dir(form))
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data  # Usa el setter para hashear
        )
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)




@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    user = User.verify_confirmation_token(token)
    if not user:
        flash('El enlace de confirmación es inválido o ha expirado', 'danger')
        return redirect(url_for('bp.login'))
    
    user.is_active = True
    db.session.commit()
    flash('Cuenta confirmada exitosamente. Ya puedes iniciar sesión.', 'success')
    return redirect(url_for('bp.login'))