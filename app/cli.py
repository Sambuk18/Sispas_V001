import click
from flask.cli import with_appcontext
from app import db
from app.models import Recibos, RecibosNew
from datetime import datetime

@click.command('migrate-recibos')
@with_appcontext
def migrate_recibos():
    """Migrar datos existentes de Recibos a RecibosNew"""
    
    def parse_date(date_str):
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt) if date_str else None
            except ValueError:
                continue
        return None
    
    def parse_numeric(num_str):
        try:
            if not num_str:
                return None
            # Elimina puntos de mil y convierte comas a punto decimal
            cleaned = num_str.replace('.', '').replace(',', '.')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    click.echo("Iniciando migración de recibos...")
    
    total = Recibos.query.count()
    processed = 0
    
    for recibo in Recibos.query.yield_per(100):  # Procesa en lotes de 100
        # Verifica si ya existe en RecibosNew
        if RecibosNew.query.filter_by(original_id=recibo.id).first():
            continue
            
        data = {
            'pronro': recibo.pronro,
            'numero': recibo.numero,
            'num_cli': recibo.num_cli,
            'planilla': recibo.planilla,
            'codigo': recibo.codigo,
            'seccion': recibo.seccion,
            'poliza': recibo.poliza,
            'endoso': recibo.endoso,
            'operacion': recibo.operacion,
            'fec_ope': parse_date(recibo.fec_ope),
            'fereal': parse_date(recibo.fereal),
            'vencuot': parse_date(recibo.vencuot),
            'vdes': parse_date(recibo.vdes),
            'vhas': parse_date(recibo.vhas),
            'moneda': recibo.moneda,
            'prima': parse_numeric(recibo.prima),
            'rec': parse_numeric(recibo.rec),
            'deradm': parse_numeric(recibo.deradm),
            'impytas': parse_numeric(recibo.impytas),
            'premio': parse_numeric(recibo.premio),
            'prerea': parse_numeric(recibo.prerea),
            'nrorec': recibo.nrorec,
            'nrocut': recibo.nrocut,
            'codpro': recibo.codpro,
            'pend': recibo.pend,
            'control_hash': recibo.control_hash,
            'sync_date': recibo.sync_date,
            'dbf_source': recibo.dbf_source,
            'original_id': recibo.id
        }
        
        new_rec = RecibosNew(**data)
        db.session.add(new_rec)
        
        processed += 1
        if processed % 100 == 0:
            db.session.commit()
            click.echo(f"Procesados {processed}/{total} recibos...")
    
    db.session.commit()
    click.echo(f"Migración completada. Total procesados: {processed} recibos")