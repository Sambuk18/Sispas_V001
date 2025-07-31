import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
basedir = Path(__file__).parent.absolute()
env_path = basedir / '.env'
load_dotenv(env_path)

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SERVER_NAME = os.environ.get('SERVER_NAME')
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'https')
    
    # Intervalo de escaneo en segundos (60 segundos = 1 minuto)
    SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 3600))
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMINS = os.environ.get('ADMINS', '').split(',')
    
    # Configuración de archivos DBF
    LOCAL_DBF_PATH = os.path.expanduser(os.environ.get('LOCAL_DBF_PATH')).split(',')
    REMOTE_DBF_PATH = os.environ.get('REMOTE_DBF_PATH').split(',')
    DBF_EXTENSIONS = os.environ.get('DBF_EXTENSIONS', '')
    DBF_DIRECTORY = os.getenv('DBF_DIRECTORY', '/home/sisflask/systema/OFICINA/emporal')
    DBF_FILES = ['con_gast', 'recibos', 'sfac_tur', 'scliente', 'cod_post', 'producto']
    DBF_DIRECTORY = os.environ.get('DBF_DIRECTORY','')
    # Otras configuraciones
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE', 10))
    LANGUAGES = os.environ.get('LANGUAGES', 'en,es').split(',')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}