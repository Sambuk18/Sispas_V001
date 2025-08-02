from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired
from flask_mail import Message
from app import db, login_manager, mail
from app.models import User, UserData, UserSession
from app.auth.forms import LoginForm, RegistrationForm, ProfileForm
import logging
logging.basicConfig(level=logging.DEBUG)

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
    timeout = request.args.get('timeout')
    if timeout:
        flash("Sesión expirada por inactividad", "warning")
        return render_template('auth/login.html')
        
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
        session_record = UserSession(user_id=current_user.id)
        db.session.add(session_record)
        db.session.commit()
        session['current_session_id'] = session_record.id  # Guarda el ID en la sesión de Flask

        return redirect(next_page or url_for('main_bp.dashboard'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    if 'current_session_id' in session:
        session_record = UserSession.query.get(session['current_session_id'])
        if session_record:
            session_record.logout_time = datetime.utcnow()
            session_record.duration_seconds = (session_record.logout_time - session_record.login_time).total_seconds()
            db.session.commit()

    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logoutauto')
@login_required
def logoutauto():
    logout_user()
    if 'current_session_id' in session:
        session_record = UserSession.query.get(session['current_session_id'])
        if session_record:
            session_record.logout_time = datetime.utcnow()
            session_record.duration_seconds = (session_record.logout_time - session_record.login_time).total_seconds()
            db.session.commit()
    flash('Has cerrado sesión correctamente.', 'success')
    return '', 204
    

    
# Ruta para el perfil del usuario actual
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Cargar datos existentes o preparar formulario vacío
    form = ProfileForm(obj=current_user.user_data)
    
    if form.validate_on_submit():
        try:
            if not current_user.user_data:
                # Crear un nuevo registro UserData con los datos del formulario
                user_data = UserData(
                    user_id=current_user.id,
                    nombres=form.nombres.data,
                    apellido=form.apellido.data,
                    cuil_dni=form.cuil_dni.data,
                    celular=form.celular.data,
                    nivel_usuario=form.nivel_usuario.data
                )
                db.session.add(user_data)
            else:
                # Actualizar el registro existente
                form.populate_obj(current_user.user_data)
            
            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar perfil: {str(e)}', 'danger')
            # Esto ayuda a debuggear - puedes removerlo en producción
            app.logger.error(f'Error al guardar perfil: {str(e)}', exc_info=True)
    
    # Para el GET, si no hay user_data, mostramos formulario vacío
    return render_template('auth/profile.html', form=form, user=current_user)

# Ruta para edición por admin (si es necesaria)
@auth_bp.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_profile(user_id):
    if not current_user.is_admin:  # Asegúrate de tener este campo en tu modelo User
        abort(403)
    
    user = User.query.get_or_404(user_id)
    form = ProfileForm(obj=user.user_data)
    
    if form.validate_on_submit():
        try:
            if not user.user_data:
                user_data = UserData(user_id=user.id)
                db.session.add(user_data)
            else:
                user_data = user.user_data
            
            form.populate_obj(user_data)
            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('auth.admin_edit_profile', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar perfil: {str(e)}', 'danger')
    
    return render_template('auth/profile.html', form=form, user=user)   


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# auth/routes.py
# Asegúrate de que las importaciones de arriba son correctas

