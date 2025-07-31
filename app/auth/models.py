from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from flask import current_app


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # Nueva columna
    token = db.Column(db.String(200), nullable=True)   # Token de verificación

    def __init__(self, email, password, is_verified=False):
        self.email = email
        self.password = password
        self.is_verified = is_verified        
        
    def generate_verification_token(self, expires_sec=3600):  # 1 hora de validez
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')  # decode para Python 3

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))  # encode para Python 3
            return User.query.get(data['user_id'])
        except (BadSignature, SignatureExpired) as e:
            current_app.logger.error(f"Error verifying token: {str(e)}")
            return None

    