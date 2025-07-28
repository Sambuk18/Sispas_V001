from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, DecimalField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="El email es requerido"),
        Email(message="Ingrese un email válido")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es requerida")
    ])
    remember = BooleanField('Recordarme')


class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[
        DataRequired("El nombre de usuario es obligatorio"),
        Length(min=4, max=25)
    ])
    email = StringField('Email', validators=[
        DataRequired("El email es obligatorio"),
        Email("Ingrese un email válido"),
        Length(max=120)
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired("La contraseña es obligatoria"),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired("Confirme su contraseña"),
        EqualTo('password', message="Las contraseñas deben coincidir")
    ])
    submit = SubmitField('Registrarse')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado')
