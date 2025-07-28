from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Recibo, Poliza, Pago
from app.forms import ReciboForm, PagoForm
from datetime import datetime
from sqlalchemy import desc

recibos_bp = Blueprint('recibos', __name__)

@recibos_bp.route('/recibos')
@login_required
def list_recibos():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todos')
    
    query = Recibo.query.join(Poliza)
    
    if estado == 'pendientes':
        query = query.filter(Recibo.estado == 'pendiente')
    elif estado == 'pagados':
        query = query.filter(Recibo.estado == 'pagado')
    elif estado == 'vencidos':
        query = query.filter(Recibo.estado == 'vencido')
    
    recibos = query.order_by(desc(Recibo.fecha_emision)).paginate(page=page, per_page=15)
    
    return render_template('recibos/list.html', 
                         recibos=recibos, 
                         estado_actual=estado)

@recibos_bp.route('/recibos/create', methods=['GET', 'POST'])
@login_required
def create_recibo():
    form = ReciboForm()
    # Dinamizar las pólizas en el formulario
    form.poliza_id.choices = [(p.id, f"{p.numero} - {p.cliente.nombre}") 
                             for p in Poliza.query.filter_by(estado='activa').all()]
    
    if form.validate_on_submit():
        recibo = Recibo(
            numero=Recibo.generar_numero(),
            poliza_id=form.poliza_id.data,
            fecha_emision=form.fecha_emision.data,
            fecha_vencimiento=form.fecha_vencimiento.data,
            monto=form.monto.data,
            estado='pendiente',
            forma_pago=form.forma_pago.data,
            observaciones=form.observaciones.data
        )
        
        db.session.add(recibo)
        db.session.commit()
        
        flash('Recibo creado exitosamente', 'success')
        return redirect(url_for('recibos.view_recibo', id=recibo.id))
    
    return render_template('recibos/create.html', form=form)

@recibos_bp.route('/recibos/<int:id>')
@login_required
def view_recibo(id):
    recibo = Recibo.query.get_or_404(id)
    return render_template('recibos/view.html', recibo=recibo)

@recibos_bp.route('/recibos/<int:id>/pago', methods=['GET', 'POST'])
@login_required
def add_pago(id):
    recibo = Recibo.query.get_or_404(id)
    form = PagoForm()
    
    if form.validate_on_submit():
        pago = Pago(
            recibo_id=id,
            fecha=form.fecha.data,
            monto=form.monto.data,
            forma_pago=form.forma_pago.data,
            referencia=form.referencia.data,
            observaciones=form.observaciones.data
        )
        
        db.session.add(pago)
        
        # Actualizar estado del recibo si está completamente pagado
        if recibo.calcular_total() + pago.monto >= recibo.monto:
            recibo.estado = 'pagado'
        
        db.session.commit()
        
        flash('Pago registrado exitosamente', 'success')
        return redirect(url_for('recibos.view_recibo', id=id))
    
    return render_template('recibos/add_pago.html', form=form, recibo=recibo)

@recibos_bp.route('/recibos/<int:id>/anular', methods=['POST'])
@login_required
def anular_recibo(id):
    recibo = Recibo.query.get_or_404(id)
    
    if recibo.estado == 'pagado':
        flash('No se puede anular un recibo ya pagado', 'danger')
    else:
        recibo.estado = 'anulado'
        db.session.commit()
        flash('Recibo anulado exitosamente', 'success')
    
    return redirect(url_for('recibos.view_recibo', id=id))

@recibos_bp.route('/recibos/generar-masivo', methods=['GET', 'POST'])
@login_required
def generar_masivo():
    if request.method == 'POST':
        polizas_ids = request.form.getlist('polizas')
        fecha_emision = datetime.strptime(request.form['fecha_emision'], '%Y-%m-%d').date()
        
        for poliza_id in polizas_ids:
            poliza = Poliza.query.get(poliza_id)
            if poliza:
                recibo = Recibo(
                    numero=Recibo.generar_numero(),
                    poliza_id=poliza.id,
                    fecha_emision=fecha_emision,
                    monto=poliza.prima,
                    estado='pendiente'
                )
                db.session.add(recibo)
        
        db.session.commit()
        flash(f'Se generaron {len(polizas_ids)} recibos exitosamente', 'success')
        return redirect(url_for('recibos.list_recibos'))
    
    # GET: Mostrar pólizas activas
    polizas = Poliza.query.filter_by(estado='activa').all()
    return render_template('recibos/generar_masivo.html', polizas=polizas)