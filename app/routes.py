from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Compania
from app.companias.forms import CompaniaForm
from app.companias import companias_bp

@companias_bp.route('/companias')
@login_required
def list_companias():
    page = request.args.get('page', 1, type=int)
    companias = Compania.query.order_by(Compania.nombre).paginate(page=page, per_page=10)
    return render_template('companias/list.html', companias=companias)

@companias_bp.route('/companias/create', methods=['GET', 'POST'])
@login_required
def create_compania():
    form = CompaniaForm()
    if form.validate_on_submit():
        compania = Compania(
            nombre=form.nombre.data,
            direccion=form.direccion.data,
            telefono=form.telefono.data,
            email=form.email.data,
            contacto=form.contacto.data,
            comision=form.comision.data
        )
        db.session.add(compania)
        db.session.commit()
        flash('Compañía creada exitosamente', 'success')
        return redirect(url_for('companias.list_companias'))
    return render_template('companias/create.html', form=form)

@companias_bp.route('/companias/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_compania(id):
    compania = Compania.query.get_or_404(id)
    form = CompaniaForm(obj=compania)
    if form.validate_on_submit():
        compania.nombre = form.nombre.data
        compania.direccion = form.direccion.data
        compania.telefono = form.telefono.data
        compania.email = form.email.data
        compania.contacto = form.contacto.data
        compania.comision = form.comision.data
        db.session.commit()
        flash('Compañía actualizada exitosamente', 'success')
        return redirect(url_for('companias.list_companias'))
    return render_template('companias/edit.html', form=form, compania=compania)

@companias_bp.route('/companias/<int:id>/delete', methods=['POST'])
@login_required
def delete_compania(id):
    compania = Compania.query.get_or_404(id)
    compania.is_active = False
    db.session.commit()
    flash('Compañía desactivada exitosamente', 'success')
    return redirect(url_for('companias.list_companias'))