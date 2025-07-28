from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)

def send_test_email():
    with app.app_context():
        msg = Message(
            'Recibo solicitado- Sistema de Seguros',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['efviskup@gmail.com']  # Cambia esto
        )
        msg.body = 'Esta es una prueba del sistema de correo configurado.'
        mail.send(msg)
        print("Email de prueba enviado!")

if __name__ == '__main__':
    send_test_email()