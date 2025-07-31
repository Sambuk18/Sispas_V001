from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User
from flask import current_app

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[
            DataRequired(message="El email es requerido"),
            Email(message="Ingrese un email válido")
        ],
        render_kw={"placeholder": "correo@ejemplo.com"}
    )
    password = PasswordField('Contraseña',
        validators=[
            DataRequired(message="La contraseña es requerida"),
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
        ],
        render_kw={"placeholder": "••••••"}
    )
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')


class RegistrationForm(FlaskForm):
    email = StringField('Email',
        validators=[
            DataRequired(message="El email es obligatorio"),
            Email(message="Ingrese un email válido"),
            Length(max=120, message="Máximo 120 caracteres")
        ],
        render_kw={"placeholder": "correo@ejemplo.com"}
    )
    password = PasswordField('Contraseña',
        validators=[
            DataRequired(message="La contraseña es obligatoria"),
            Length(min=6, message="Mínimo 6 caracteres")
        ],
        render_kw={"placeholder": "••••••"}
    )
    confirm_password = PasswordField('Confirmar Contraseña',
        validators=[
            DataRequired(message="Confirme su contraseña"),
            EqualTo('password', message="Las contraseñas deben coincidir")
        ],
        render_kw={"placeholder": "••••••"}
    )
    submit = SubmitField('Registrarse')

    def validate_email(self, email):
        if current_app.config.get('TESTING'):
            return
            
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado. ¿Olvidaste tu contraseña?')