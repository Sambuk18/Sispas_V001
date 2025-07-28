from flask import current_app
from flask_mail import Message
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        current_app.mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_confirmation_email(user):
    from flask import url_for, render_template
    token = user.get_confirmation_token()
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    
    subject = "Confirma tu cuenta - Sistema Seguros"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    recipients = [user.email]
    
    text_body = render_template('auth/email/confirm.txt', user=user, confirm_url=confirm_url)
    html_body = render_template('auth/email/confirm.html', user=user, confirm_url=confirm_url)
    
    send_email(subject, sender, recipients, text_body, html_body)