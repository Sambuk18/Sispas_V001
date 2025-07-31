from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired
from flask_mail import Message
from app import db, login_manager, mail
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, template_folder='templates')

def generate_verification_token(email):
    """Genera un token de verificación seguro"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_verification_token(token, max_age=3600):
    """Verifica el token de verificación"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=max_age)
        return email
    except (BadSignature, SignatureExpired):
        return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este correo electrónico ya está registrado.', 'danger')
            return redirect(url_for('auth.register'))

        # Crear nuevo usuario
        new_user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Generar y enviar token de verificación
        token = generate_verification_token(new_user.email)
        verification_url = url_for(
            'auth.verify_email',
            token=token,
            _external=True,
            _scheme='https'  # Fuerza HTTPS en producción
        )

        # Configurar y enviar email
        msg = Message(
            'Verifica tu cuenta',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[new_user.email]
        )
        msg.body = f'''¡Gracias por registrarte!
        
Para completar tu registro, por favor verifica tu correo electrónico haciendo clic en el siguiente enlace:

{verification_url}

Este enlace expirará en 1 hora.

Si no solicitaste este registro, por favor ignora este mensaje.
'''
        mail.send(msg)

        flash('Se ha enviado un correo de verificación. Por favor revisa tu bandeja de entrada.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    # Depuración inicial
    current_app.logger.info(f"Token recibido: {token}")
    current_app.logger.info(f"Intentando verificar token con SECRET_KEY: {current_app.config['SECRET_KEY']}")

    email = verify_verification_token(token)
    if not email:
        current_app.logger.error("Token inválido o expirado")
        flash('El enlace de verificación es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.register'))

    user = User.query.filter_by(email=email).first()
    if not user:
        current_app.logger.error(f"Usuario con email {email} no encontrado")
        flash('Error al verificar tu cuenta. Por favor regístrate nuevamente.', 'danger')
        return redirect(url_for('auth.register'))

    if user.is_verified:
        flash('Tu cuenta ya está verificada. Puedes iniciar sesión.', 'info')
    else:
        user.is_verified = True
        user.verified_on = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Usuario {user.email} verificado exitosamente")
        flash('¡Cuenta verificada con éxito! Ahora puedes iniciar sesión.', 'success')

    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Correo electrónico o contraseña incorrectos.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_verified:
            flash('Por favor verifica tu correo electrónico antes de iniciar sesión.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main_bp.dashboard'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))