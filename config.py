import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-segura'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://usuariosyspas:migu3lit0chhavela@localhost/seguros_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    DBF_FOLDER = "~/systema/OFICINA/emporal"  # Cambiar por tu ruta real    
    DBF_EXTENSIONS = ['.dbf', '.DBF', '.fbf', '.FBF']  # Agrega todas las variantes que necesites
    DBF_FILES = ['con_gast.dbf', 'ctacte.dbf', 'recibos.dbf', 'sfac_tur.dbf',
        'scliente.dbf', 'printer.dbf', 'cod_post.dbf',
         'producto.dbf',]  # o lo que corresponda

    # Configuración de Email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'organizacionsispas@gmail.com'
    MAIL_PASSWORD = 'zido ixls ucpe caxf'
    MAIL_DEFAULT_SENDER = 'organizacionsispas@gmail.com'



    ADMINS = ['organizacionsispas@gmail.com']  # Actualiza con tu email admin
    POSTS_PER_PAGE = 10
    LANGUAGES = ['en', 'es']