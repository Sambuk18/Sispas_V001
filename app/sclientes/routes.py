# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from models import SCliente
from forms import SClienteForm
from flask import Blueprint

bp = Blueprint('sclientes', __name__)


@bp.route('/clientes')
def list_clientes():
    clientes = SCliente.query.all()
    return render_template('scliente/teplates/list.html', clientes=clientes)

@bp.route('/clientes/new', methods=['GET', 'POST'])
def new_cliente():
    form = SClienteForm()
    if form.validate_on_submit():
        cliente = SCliente(**form.data)
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado', 'success')
        return redirect(url_for('list_clientes'))
    return render_template('scliente/templates/form.html', form=form)

@bp.route('/clientes/<int:id>/edit', methods=['GET', 'POST'])
def edit_cliente(id):
    cliente = SCliente.query.get_or_404(id)
    form = SClienteForm(obj=cliente)
    if form.validate_on_submit():
        form.populate_obj(cliente)
        db.session.commit()
        flash('Cliente actualizado', 'success')
        return redirect(url_for('list_clientes'))
    return render_template('scliente/templates/form.html', form=form, cliente=cliente)

@bp.route('/clientes/<int:id>/delete', methods=['POST'])
def delete_cliente(id):
    cliente = SCliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado', 'success')
    return redirect(url_for('list_clientes'))
