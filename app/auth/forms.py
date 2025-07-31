from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField 
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User, UserData
from flask import current_app

class ProfileForm(FlaskForm):
    nombres = StringField(
        'Nombre', 
        validators=[DataRequired(), Length(max=50)],
        default='Nombre',  # Valor por defecto para nombres
        render_kw={"placeholder": "Ingrese sus nombres"}
    )
    
    apellido = StringField(
        'Apellido', 
        validators=[DataRequired(), Length(max=50)],
        default='Apellido',  # Valor por defecto para apellido
        render_kw={"placeholder": "Ingrese su apellido"}
    )
    cuil_dni = StringField(
        'CUIL/DNI', 
        validators=[DataRequired(), Length(max=20)],
        default='20-12345678-0',  # Valor por defecto para CUIL/DNI
        render_kw={"placeholder": "Ej: 20-12345678-0"}
    )
    celular = StringField(
        'Nº de Celular', 
        validators=[DataRequired(), Length(max=15)],
        default='3644555555',  # Valor por defecto para celular
        render_kw={"placeholder": "Ej: 3511234567"}
    )
    
    nivel_usuario = SelectField(
        'Nivel de Usuario',
        choices=[
            (9, 'Visitante'), 
            (1, 'Asegurado'), 
            (2, 'Productor')
        ],
        coerce=int,
        validators=[DataRequired()],
        default=9,  # Valor por defecto ya establecido
        render_kw={"class": "form-select"}  # Ejemplo de atributo adicional
    )
    
    submit = SubmitField(
        'Actualizar Perfil',
        render_kw={"class": "btn btn-primary"}  # Clases de Bootstrap
    )


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