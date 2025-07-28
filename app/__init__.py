from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configuración de LoginManager
    login_manager.login_view = 'auth_bp.login'


    
    

    # Registrar todos los blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.asegurados.routes import bp as asegurados_bp  
    from app.categorias.routes import bp as categorias_bp    
    from app.clientes.routes import bp as clientes_bp
    from app.cobranzas.routes import bp as cobranzas_bp
    from app.companias.routes import bp as companias_bp
    from app.gastos.routes import bp as gastos_bp
    from app.liquidaciones.routes import bp as liquidaciones_bp
    from app.mecanicos.routes import bp as mecanicos_bp
    from app.pagos.routes import bp as pagos_bp
    from app.productos.routes import bp as productos_bp
    from app.proveedores.routes import bp as proveedores_bp
    from app.recibos.routes import bp as recibos_bp
    from app.recibos.dbf_sync import dbf_sync_bp
    from app.taller.routes import bp as taller_bp
    from app.vendedores.routes import bp as vendedores_bp
    

    # Registrar en la app
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)  # Sin prefijo: maneja '/' y '/dashboard'
    app.register_blueprint(asegurados_bp, url_prefix='/asegurados')
    app.register_blueprint(categorias_bp, url_prefix='/categorias')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(cobranzas_bp, url_prefix='/cobranzas')
    app.register_blueprint(companias_bp, url_prefix='/companias')
    app.register_blueprint(gastos_bp, url_prefix='/gastos')
    app.register_blueprint(liquidaciones_bp, url_prefix='/liquidaciones')
    app.register_blueprint(mecanicos_bp, url_prefix='/mecanicos')
    app.register_blueprint(pagos_bp, url_prefix='/pagos')
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores')
    app.register_blueprint(recibos_bp, url_prefix='/recibos')
    app.register_blueprint(dbf_sync_bp, url_prefix='/recibos')
    app.register_blueprint(taller_bp, url_prefix='/taller')
    app.register_blueprint(vendedores_bp, url_prefix='/vendedores')
    

    return app
