from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from app import db  # Solo importamos db aquí
from app import login_manager  # Importamos login_manager desde __init__.py
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

##### hay  que eliminar la tabla cajas, cuentas,

class Sfac_tur(db.Model):
    __tablename__ = 'sfac_tur'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tip_fac = db.Column(db.Text)         # Tipo de factura
    fec_fac = db.Column(db.Text)         # Fecha factura
    nro_fac = db.Column(db.Text)         # Número factura
    tur_fac = db.Column(db.Text)         # Tur factura
    fecpue = db.Column(db.Text)          # Fecha puesta
    fecvirt = db.Column(db.Text)         # Fecha virtual
    fecrea = db.Column(db.Text)          # Fecha creación
    fec_rec = db.Column(db.Text)         # Fecha recibo
    recibo = db.Column(db.Text)          # Recibo
    basico = db.Column(db.Text)          # Básico
    com_ion = db.Column(db.Text)         # Comisión
    net_o = db.Column(db.Text)           # Neto
    iva = db.Column(db.Text)             # IVA
    iva_noins = db.Column(db.Text)       # IVA no inscripto
    sdat_cli = db.Column(db.Text)        # Datos cliente
    nro_cli = db.Column(db.Text)         # Número cliente
    nro_cuo = db.Column(db.Text)         # Número cuota
    nro_nic = db.Column(db.Text)         # Número NIC
    polizan = db.Column(db.Text)         # Póliza 1
    poliza2 = db.Column(db.Text)         # Póliza 2
    recint = db.Column(db.Text)          # Recinto
    estado = db.Column(db.Text)          # Estado
    proint = db.Column(db.Text)          # Proint
    control_hash = db.Column(db.String(32), unique=True, nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    dbf_source = db.Column(db.String(255))




class Scliente(db.Model):
    __tablename__ = 'scliente'
   
    # Campos exactamente como en la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nro_cli = db.Column(db.Text)
    num_soc = db.Column(db.Text)
    act_ivo = db.Column(db.Text)
    ape_cli = db.Column(db.Text)
    nom_cli = db.Column(db.Text)
    nombrer = db.Column(db.Text)
    dom_cli = db.Column(db.Text)
    loc_cli = db.Column(db.Text)
    postal = db.Column(db.Text)
    pro_cli = db.Column(db.Text)
    con_doc = db.Column(db.Text)
    doc_cli = db.Column(db.Text)
    nac_nal = db.Column(db.Text)
    tip_cui = db.Column(db.Text)
    cuit = db.Column(db.String(20))
    con_iva = db.Column(db.Text)
    nac_cli = db.Column(db.Text)
    est_civ = db.Column(db.Text)
    ocu_cli = db.Column(db.Text)
    act_cli = db.Column(db.Text)
    tel_fax = db.Column(db.Text)
    cia_ase = db.Column(db.Text)
    cip_cli = db.Column(db.Text)
    cip_cl2 = db.Column(db.Text)
    cip_cl3 = db.Column(db.Text)
    cip_end = db.Column(db.Text)
    cip_res = db.Column(db.Text)
    pol_iza = db.Column(db.Text)
    pol_iz2 = db.Column(db.Text)
    des_de = db.Column(db.Text)
    has_ta = db.Column(db.Text)
    cob_ert = db.Column(db.Text)
    for_pag = db.Column(db.Text)
    pat_ent = db.Column(db.Text)
    cha_sis = db.Column(db.Text)
    ano_mod = db.Column(db.Text)
    mot_or = db.Column(db.Text)
    val_or = db.Column(db.Text)
    uso_vei = db.Column(db.Text)
    res_civ = db.Column(db.Text)
    ant_cip = db.Column(db.Text)
    nro_rec = db.Column(db.Text)
    can_cuo = db.Column(db.Text)
    imp_cuo = db.Column(db.Text)
    tot_pol = db.Column(db.Text)
    pre_mio = db.Column(db.Text)
    recargos = db.Column(db.Text)
    deremi = db.Column(db.Text)
    tasas = db.Column(db.Text)
    nuevo = db.Column(db.Text)
    pri_ma = db.Column(db.Text)
    mar_ca = db.Column(db.Text)
    tip_o = db.Column(db.Text)
    zon_a = db.Column(db.Text)
    pro_duc = db.Column(db.Text)
    age_nte = db.Column(db.Text)
    acr_pre = db.Column(db.Text)
    dir_acr = db.Column(db.Text)
    cta_cte = db.Column(db.Text)
    cobranza = db.Column(db.Text)
    sec_cion = db.Column(db.Text)
    siniestr = db.Column(db.Text)
    fec_emic = db.Column(db.Text)
    control_hash = db.Column(db.String(32), unique=True, nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    dbf_source = db.Column(db.String(255))


    def __repr__(self):
        return f'<Scliente {self.nro_cli} - {self.ape_cli}, {self.nom_cli}>'


class Cod_post(db.Model):
    __tablename__ = 'cod_post'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    n_posta = db.Column(db.Text)  # Nombre o código de la postal
    nro_pos = db.Column(db.Text)  # Número postal (código)
    nom_loc = db.Column(db.Text)  # Nombre de la localidad
    pro_vin = db.Column(db.Text)  # Provincia
    control_hash = db.Column(db.String(32), unique=True, nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    dbf_source = db.Column(db.String(255))

    def __repr__(self):
        return f'<CodigoPostal {self.nro_pos} - {self.nom_loc}>'




class Con_gast(db.Model):
    __tablename__ = 'con_gast'    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gas_numero = db.Column(db.Text)    # Número de gasto
    gas_numnom = db.Column(db.Text)   # Número/nombre asociado
    gas_codigo = db.Column(db.Text)   # Código del gasto
    gas_entrad = db.Column(db.Text)   # Entrada/dato adicional
    gas_fe_com = db.Column(db.Text)    # Fecha de comprobante (considerar DateTime)
    gas_nrecib = db.Column(db.Text)    # Número de recibo
    des_gasto = db.Column(db.Text)    # Descripción del gasto
    gas_itotal = db.Column(db.Text)    # Importe total (considerar Numeric)
    planilla = db.Column(db.Text)      # Planilla asociada
    operacion = db.Column(db.Text)    # Operación relacionada
    neto = db.Column(db.Text)         # Neto (considerar Numeric)
    iva = db.Column(db.Text)          # IVA (considerar Numeric)
    otro_recar = db.Column(db.Text)   # Otros recargos (considerar Numeric)
    varios = db.Column(db.Text)       # Varios/datos adicionales
    estado = db.Column(db.Text)       # Estado del gasto
    proint = db.Column(db.Text)       # Proint (posiblemente proveedor/intermediario)
    client = db.Column(db.Text)       # Cliente asociado
    control_hash = db.Column(db.String(32), unique=True, nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    dbf_source = db.Column(db.String(255))

    def __repr__(self):
        return f'<Con_gast {self.gas_numero} - {self.des_gasto}>'

class CuentaCorriente(db.Model):
    __tablename__ = 'ctacte'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asegur = db.Column(db.Text)      # Aseguradora/Compañía
    asedet = db.Column(db.Text)      # Detalle aseguradora
    pol = db.Column(db.Text)         # Póliza relacionada
    cta = db.Column(db.Text)         # Cuenta/Número de cuenta
    debepag = db.Column(db.Text)     # Débito/Pago (D/H)
    monto = db.Column(db.Text)       # Monto (considerar Numeric)
    sald = db.Column(db.Text)        # Saldo (considerar Numeric)
    entre = db.Column(db.Text)       # Entregado/Recibido por
    fech = db.Column(db.Text)        # Fecha (considerar DateTime)
    numch = db.Column(db.Text)       # Número de cheque
    patente = db.Column(db.Text)     # Patente (vehículo)
    pvta = db.Column(db.Text)        # Punto de venta
    nrec = db.Column(db.Text)        # Número de recibo
    marc = db.Column(db.Text)        # Marca (vehículo)
    mode = db.Column(db.Text)        # Modelo (vehículo)
    ano = db.Column(db.Text)         # Año (vehículo)
    control_hash = db.Column(db.String(32), unique=True, nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    dbf_source = db.Column(db.String(255))

    def __repr__(self):
        return f'<CuentaCorriente {self.pol} - {self.asegur}>'


class Recibos(db.Model):
    __tablename__ = 'recibos'  # Asumo que el nombre de la tabla es 'recibos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pronro = db.Column(db.Text)
    numero = db.Column(db.Text)
    num_cli = db.Column(db.Text)
    planilla = db.Column(db.Text)
    codigo = db.Column(db.String(20))
    seccion = db.Column(db.Text)
    poliza = db.Column(db.Text)
    endoso = db.Column(db.Text)
    operacion = db.Column(db.Text)
    fec_ope = db.Column(db.Text)  # Considerar convertirlo a DateTime si el formato es consistente
    fereal = db.Column(db.Text)   # Considerar convertirlo a DateTime
    vencuot = db.Column(db.Text)  # Considerar convertirlo a DateTime
    vdes = db.Column(db.Text)     # Considerar convertirlo a DateTime
    vhas = db.Column(db.Text)     # Considerar convertirlo a DateTime
    moneda = db.Column(db.Text)
    prima = db.Column(db.Text)    # Considerar convertirlo a Numeric si son valores monetarios
    rec = db.Column(db.Text)      # Considerar convertirlo a Numeric
    deradm = db.Column(db.Text)   # Considerar convertirlo a Numeric
    impytas = db.Column(db.Text)  # Considerar convertirlo a Numeric
    premio = db.Column(db.Text)   # Considerar convertirlo a Numeric
    prerea = db.Column(db.Text)   # Considerar convertirlo a Numeric
    nrorec = db.Column(db.Text)
    nrocut = db.Column(db.Text)
    codpro = db.Column(db.Text)
    pend = db.Column(db.Text)
    control_hash = db.Column(db.String(32), unique=True, nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    dbf_source = db.Column(db.String(255))

    def __repr__(self):
        return f'<Recibos {self.numero} - {self.codigo}>'


class Producto(db.Model):
    __tablename__ = 'producto'
    
    # Campos exactamente como en la estructura de la tabla
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num = db.Column(db.Text)          # Número de producto
    apn = db.Column(db.Text)          # Apellido y nombre
    dir = db.Column(db.Text)          # Dirección
    loc = db.Column(db.Text)          # Localidad
    pro = db.Column(db.Text)          # Provincia
    cop = db.Column(db.Text)          # Código postal
    dni = db.Column(db.String(20))    # DNI (mantiene varchar(20))
    cui = db.Column(db.Text)          # CUIT/CUIL
    tel = db.Column(db.Text)          # Teléfono
    cel = db.Column(db.Text)          # Celular
    com = db.Column(db.Text)          # Comentario 1
    co2 = db.Column(db.Text)          # Comentario 2
    control_hash = db.Column(db.String(32), unique=True, nullable=False)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    dbf_source = db.Column(db.String(255))

    def __repr__(self):
        return f'<Producto {self.num} - {self.apn}>'

class UserData(db.Model):
    __tablename__ = 'user_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  #sdfdsfsd  Añadir autoincrement
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nombres = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    cuil_dni = db.Column(db.String(15), nullable=False)
    celular = db.Column(db.String(15))
    nivel_usuario = db.Column(db.Integer, nullable=False)
    
    # Relación
    user = db.relationship('User', back_populates='user_data')
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # Nueva columna
    token = db.Column(db.String(200), nullable=True)   # Token de verificación

# Nueva relación con la tabla UserData
    user_data = db.relationship('UserData', back_populates='user', uselist=False)

    def __init__(self, email, password, is_verified=False):
        self.email = email
        self.password = password
        self.is_verified = is_verified        
        
    def generate_verification_token(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
            return User.query.get(user_id)
        except:
            return None


class DBFUpdateLog(db.Model):
    """Modelo para registrar las actualizaciones en la base de datos"""
    __tablename__ = 'dbf_update_logs'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    operation = Column(String(50))  # 'copied', 'skipped', 'error'
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(500))
    

# Cargador de usuario requerido por Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Compania(db.Model):
    __tablename__ = 'companias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contacto = db.Column(db.String(100))
    comision = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    productos = db.relationship('Productos', backref='compania', lazy='dynamic')
    
    def __repr__(self):
        return f'<Compania {self.nombre}>'

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    productos = db.relationship('Productos', backref='categoria', lazy='dynamic')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class Productos(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    ###categoria_producto = db.Column(db.String(100))  # Categoría del producto
    precio_base = db.Column(db.Float, default=0.0)
    comision = db.Column(db.Float, default=0.0)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    compania_id = db.Column(db.Integer, db.ForeignKey('companias.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    polizas = db.relationship('Poliza', backref='productos', lazy='dynamic')
    
    def __repr__(self):
        return f'<Productos {self.nombre}>'

class Clientes(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(10))  # DNI, CUIT, etc.
    documento = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    fecha_nacimiento = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    polizas = db.relationship('Poliza', backref='cliente', lazy='dynamic')
    vehiculos = db.relationship('Vehiculo', backref='cliente', lazy='dynamic')
    
    def __repr__(self):
        return f'<Clientes {self.nombre} {self.apellido}>'

class Asegurado(db.Model):
    __tablename__ = 'asegurados'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(10))
    documento = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    fecha_nacimiento = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    polizas = db.relationship('Poliza', backref='asegurado', lazy='dynamic')
    
    def __repr__(self):
        return f'<Asegurado {self.nombre} {self.apellido}>'

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True)
    tipo_documento = db.Column(db.String(10))
    documento = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    comision = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ##ventas = db.relationship('Venta', backref='vendedor', lazy='dynamic')
    
    def __repr__(self):
        return f'<Vendedor {self.nombre} {self.apellido}>'

class Poliza(db.Model):
    __tablename__ = 'polizas'
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'))
    numero = db.Column(db.String(50), unique=True, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    asegurado_id = db.Column(db.Integer, db.ForeignKey('asegurados.id'))
    fecha_emision = db.Column(db.Date, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    prima = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='activa')  # activa, vencida, cancelada
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recibos = db.relationship('Recibo', backref='poliza', lazy='dynamic')
    
    def __repr__(self):
        return f'<Poliza {self.numero}>'

class Recibo(db.Model):
    __tablename__ = 'recibosdb'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    poliza_id = db.Column(db.Integer, db.ForeignKey('polizas.id'))
    fecha_emision = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date)
    monto = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagado, vencido, cancelado
    forma_pago = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pagos = db.relationship('Pago', backref='recibo', lazy='dynamic')
    
    def __repr__(self):
        return f'<Recibo {self.numero}>'
    def saldo(self):
        return self.monto - self.calcular_total()
    
    def porcentaje_pagado(self):
        if self.monto == 0:
            return 100
        return (self.calcular_total() / self.monto) * 100
    
    @staticmethod
    def generar_numero():
        # Genera un número de recibo secuencial con prefijo y ceros a la izquierda
        ultimo = Recibo.query.order_by(Recibo.id.desc()).first()
        nuevo_num = 1 if not ultimo else ultimo.id + 1
        return f"REC-{nuevo_num:08d}"
    
    def actualizar_estado(self):
        if self.porcentaje_pagado() >= 100:
            self.estado = 'pagado'
        elif self.fecha_vencimiento and datetime.now().date() > self.fecha_vencimiento:
            self.estado = 'vencido'
        else:
            self.estado = 'pendiente'
        db.session.commit()
        

class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    recibo_id = db.Column(db.Integer, db.ForeignKey('recibosdb.id'))
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    forma_pago = db.Column(db.String(50), nullable=False)  # efectivo, transferencia, etc.
    referencia = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pago {self.id}>'

class Taller(db.Model):
    __tablename__ = 'taller'
    
    id = db.Column(db.Integer, primary_key=True)
    orden_numero = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'))
    fecha_ingreso = db.Column(db.Date, nullable=False)
    fecha_egreso = db.Column(db.Date)
    estado = db.Column(db.String(20), default='ingresado')  # ingresado, en_reparacion, terminado, entregado
    descripcion = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('TallerItem', backref='taller', lazy='dynamic')
    
    
    def __repr__(self):
        return f'<Taller {self.orden_numero}>'

class TallerItem(db.Model):
    __tablename__ = 'taller_items'
    
    id = db.Column(db.Integer, primary_key=True)
    taller_id = db.Column(db.Integer, db.ForeignKey('taller.id'))
    tipo = db.Column(db.String(50), nullable=False)  # mano_obra, repuesto, etc.
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Float, default=1.0)
    precio_unitario = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, default=21.0)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('mecanicos.id'))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TallerItem {self.id}>'

class Mecanico(db.Model):
    __tablename__ = 'mecanicos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    especialidad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    comision = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('TallerItem', backref='mecanico', lazy='dynamic')
    
    def __repr__(self):
        return f'<Mecanico {self.nombre} {self.apellido}>'

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contacto = db.Column(db.String(100))
    cuit = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('TallerItem', backref='proveedor', lazy='dynamic')
    gastos = db.relationship('Gasto', backref='proveedor', lazy='dynamic')
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    año = db.Column(db.Integer)
    patente = db.Column(db.String(20), unique=True)
    chasis = db.Column(db.String(50))
    motor = db.Column(db.String(50))
    color = db.Column(db.String(30))
    km = db.Column(db.Integer)
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    polizas = db.relationship('Poliza', backref='vehiculo', lazy='dynamic')
    ordenes = db.relationship('Taller', backref='vehiculo', lazy='dynamic')
    
    
    def __repr__(self):
        return f'<Vehiculo {self.marca} {self.modelo} {self.patente}>'

class Gasto(db.Model):
    __tablename__ = 'gastos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # alquiler, servicios, etc.
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    iva = db.Column(db.Float, default=21.0)
    descripcion = db.Column(db.Text)
    forma_pago = db.Column(db.String(50))
    referencia = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Gasto {self.tipo} {self.monto}>'

class Liquidacion(db.Model):
    __tablename__ = 'liquidaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # vendedor, compania, taller
    referencia_id = db.Column(db.Integer)  # ID del vendedor, compañía, etc.
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    monto_total = db.Column(db.Float, nullable=False)
    comision_total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, pagada
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pagos = db.relationship('LiquidacionPago', backref='liquidacion', lazy='dynamic')
    
    def __repr__(self):
        return f'<Liquidacion {self.numero}>'

class LiquidacionPago(db.Model):
    __tablename__ = 'liquidacion_pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    liquidacion_id = db.Column(db.Integer, db.ForeignKey('liquidaciones.id'))
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    forma_pago = db.Column(db.String(50), nullable=False)
    referencia = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LiquidacionPago {self.id}>'
    
    