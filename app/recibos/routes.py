from flask import Blueprint, render_template, request, send_file
from sqlalchemy import text
from app import db
from datetime import datetime
from datetime import date
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PyPDF2 import PdfReader, PdfWriter
import os
import re
from flask import send_file, current_app
import locale

bp = Blueprint('recibos', __name__, template_folder='templates')

# Configurar la localización a Argentina
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')

# Definir ruta base
base_path = "/home/sisflask/systema/COMPROBANTES/SistemaNuevo"

# Establecer configuración regional para nombres en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'es_ES')  # Alternativa si es necesario

# Obtener fecha actual
hoy = datetime.now()
anio = hoy.strftime("%Y")
mes = hoy.strftime("%m")
dia_nombre = hoy.strftime("%A%dde%Bde%Y").capitalize()

# Construir ruta completa
ruta_destino = os.path.join(base_path, anio, mes, dia_nombre)
os.makedirs(ruta_destino, exist_ok=True)


@bp.route('/recibos', methods=['GET', 'POST'])
def list_recibos():
    recibos = []
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        # tu lógica de consulta aquí con esa fecha
    else:
        fecha = date.today().isoformat()  # Valor por defecto: hoy
    if request.method == 'POST':
        fecha = request.form['fecha']
        try:
            fecha_mysql = datetime.strptime(fecha, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            fecha_mysql = fecha
        query = text("""
            SELECT 
                CONCAT(LPAD(recibos.pronro, 4, '0'), '-', LPAD(recibos.numero, 8, '0')) AS recibo_completo,
                DATE_FORMAT(recibos.fec_ope, '%d/%m/%Y') AS fec_ope,
                scliente.cia_ase,
                con_gast.des_gasto,
                scliente.dom_cli,
                scliente.loc_cli,
                scliente.pat_ent,
                scliente.mar_ca,
                scliente.tip_o,
                scliente.ano_mod,
                producto.apn,
                con_gast.gas_entrad,
                recibos.poliza,
                DATE_FORMAT(recibos.vencuot, '%d/%m/%Y') AS vencuot,
                DATE_FORMAT(recibos.vdes, '%d/%m/%Y') AS vdes,
                DATE_FORMAT(recibos.vhas, '%d/%m/%Y') AS vhas,
                recibos.premio
            FROM 
                con_gast
                JOIN recibos ON con_gast.proint = recibos.pronro AND con_gast.gas_nrecib = recibos.numero
                JOIN scliente ON scliente.nro_cli = recibos.num_cli
                JOIN producto ON producto.num = recibos.pronro
            WHERE 
                DATE(recibos.fec_ope) = :fecha
            ORDER BY 
                recibos.fec_ope DESC;
        """)
        result = db.session.execute(query, {'fecha': fecha_mysql})
        recibos = [row._asdict() for row in result]
    return render_template('consulta_recibos.html', recibos=recibos, fecha=request.form.get('fecha'), current_date=date.today().isoformat())

@bp.route('/generar_pdf_debe', methods=['POST'])
def generar_pdf_debe():
    datos = request.form.to_dict()
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    premio_valor = float(datos.get('premio', 0))
    premio_formateado = locale.currency(premio_valor, symbol=True, grouping=True)
 
    for campo_fecha in ['fec_ope', 'vdes', 'vhas', 'vencuot']:
        if campo_fecha in datos:
            datos[campo_fecha] = formatear_fecha(datos[campo_fecha])

    premio_str = datos.get('premio', '0')
    try:
        premio_numero = float(premio_str.replace(',', '.'))
    except ValueError:
        premio_numero = 0.0

    premio_formateado = locale.currency(premio_numero, symbol=True, grouping=True)
    premio_en_letras = numero_a_letras(premio_numero)

    can.setFont("Helvetica", 12)
    can.drawString(420, 783, f"{datos.get('fec_ope', '')}")
    can.drawString(420, 757, f"{datos.get('recibo_completo', '')}")
    can.setFont("Helvetica", 10)
    can.drawString(102, 718, f"{datos.get('des_gasto', '')}")
    can.drawString(102, 696, f"{datos.get('dom_cli', '')}")
    can.drawString(102, 676, f"{datos.get('loc_cli', '')}")
    can.drawString(429, 696, f"{datos.get('pat_ent', '')}")
    can.drawString(342, 718, f"{datos.get('mar_ca', '')}")
    can.drawString(342, 676, f"{datos.get('tip_o', '')}")
    can.drawString(342, 696, f"{datos.get('ano_mod', '')}")
    can.drawString(50, 628, f"{datos.get('poliza', '')}")
    can.drawString(47, 608, f"{datos.get('cia_ase', '')}")
    can.drawString(320, 618, f"{datos.get('vencuot', '')}")
    can.drawString(129, 618, f"{datos.get('vdes', '')}")
    can.drawString(220, 618, f"{datos.get('vhas', '')}")
    can.setFont("Helvetica", 15)
    can.drawString(420, 618, premio_formateado)
    can.setFont("Helvetica", 11)
    can.drawString(48, 580, premio_en_letras)

    # can.saveState()
    # can.setFont("Helvetica-Bold", 28)
    # can.setFillColorRGB(0.6, 0.6, 0.6)
    # can.setFillAlpha(0.3)
    # can.translate(180, 520)
    # can.rotate(20)
    # can.drawCentredString(0, 29, "PAGADO")
    # can.drawCentredString(0, 0, datetime.now().strftime("%d/%m/%Y"))
    # can.restoreState()

    # can.saveState()
    # can.setFillAlpha(1.0)
    # ruta_firma = os.path.join(current_app.root_path, 'static', 'img', 'firma3.png')
    # can.drawImage(ruta_firma, 190, 500, width=150, height=150, mask='auto')
    # can.restoreState()

    can.save()
    packet.seek(0)

    ruta_pdf = os.path.join(current_app.root_path, 'static', 'pdf', 'RecibosOficial9.pdf')
    existing_pdf = PdfReader(open(ruta_pdf, "rb"))
    output = PdfWriter()
    new_pdf = PdfReader(packet)

    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    # Armar nombre del archivo base
    
    
    des_gasto = datos.get('des_gasto', 'cliente').strip().replace(" ", "_").replace(",", "").replace(".", "")
    pat_ent = datos.get('pat_ent', 'vehiculo').strip().replace(" ", "_")
    nombre_archivo = f"{des_gasto}_{pat_ent}.pdf"
    #nombre_archivo = f"{datos.get('des_gasto')}_{datos.get('pat_ent')}.pdf"
    ruta_completa = os.path.join(ruta_destino, nombre_archivo)

    # Si el archivo ya existe, agregar _copy1, _copy2, etc.
    contador = 1
    nombre_base, extension = os.path.splitext(nombre_archivo)
    while os.path.exists(ruta_completa):
        nombre_archivo = f"{nombre_base}_copy{contador}{extension}"
        ruta_completa = os.path.join(ruta_destino, nombre_archivo)
        contador += 1

    # Guardar el archivo en el servidor
    with open(ruta_completa, 'wb') as f:
        f.write(output_stream.read())

    # Reiniciar el puntero del stream para enviarlo al navegador
    output_stream.seek(0)

    
    return send_file(
            output_stream,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/pdf'
    )

@bp.route('/enviar_pdf', methods=['POST'])
def enviar_pdf():
    # lógica de envío por mail
    ...

@bp.route('/generar_pdf', methods=['POST'])
def generar_pdf():
    datos = request.form.to_dict()
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    premio_valor = float(datos.get('premio', 0))
    premio_formateado = locale.currency(premio_valor, symbol=True, grouping=True)
    # Obtener y sanitizar el nombre de archivo
    des_gasto = datos.get('des_gasto', 'cliente').strip().replace(" ", "_")
    pat_ent = datos.get('pat_ent', 'vehiculo').strip().replace(" ", "_")
    nombre_archivo = f"{des_gasto}_{pat_ent}.pdf"

    # Opcional: eliminar caracteres no alfanuméricos
    nombre_archivo = re.sub(r'[^a-zA-Z0-9_.-]', '', nombre_archivo)

    for campo_fecha in ['fec_ope', 'vdes', 'vhas', 'vencuot']:
        if campo_fecha in datos:
            datos[campo_fecha] = formatear_fecha(datos[campo_fecha])

    premio_str = datos.get('premio', '0')
    try:
        premio_numero = float(premio_str.replace(',', '.'))
    except ValueError:
        premio_numero = 0.0

    premio_formateado = locale.currency(premio_numero, symbol=True, grouping=True)
    premio_en_letras = numero_a_letras(premio_numero)

    can.setFont("Helvetica", 12)
    can.drawString(420, 783, f"{datos.get('fec_ope', '')}")
    can.drawString(420, 757, f"{datos.get('recibo_completo', '')}")
    can.setFont("Helvetica", 10)
    can.drawString(102, 718, f"{datos.get('des_gasto', '')}")
    can.drawString(102, 696, f"{datos.get('dom_cli', '')}")
    can.drawString(102, 676, f"{datos.get('loc_cli', '')}")
    can.drawString(429, 696, f"{datos.get('pat_ent', '')}")
    can.drawString(342, 718, f"{datos.get('mar_ca', '')}")
    can.drawString(342, 676, f"{datos.get('tip_o', '')}")
    can.drawString(342, 696, f"{datos.get('ano_mod', '')}")
    can.drawString(50, 628, f"{datos.get('poliza', '')}")
    can.drawString(47, 608, f"{datos.get('cia_ase', '')}")
    can.drawString(320, 618, f"{datos.get('vencuot', '')}")
    can.drawString(129, 618, f"{datos.get('vdes', '')}")
    can.drawString(220, 618, f"{datos.get('vhas', '')}")
    can.setFont("Helvetica", 15)
    can.drawString(420, 618, premio_formateado)
    can.setFont("Helvetica", 11)
    can.drawString(48, 580, premio_en_letras)

    can.saveState()
    can.setFont("Helvetica-Bold", 28)
    can.setFillColorRGB(0.6, 0.6, 0.6)
    can.setFillAlpha(0.3)
    can.translate(180, 520)
    can.rotate(20)
    can.drawCentredString(0, 29, "PAGADO")
    can.drawCentredString(0, 0, datetime.now().strftime("%d/%m/%Y"))
    can.restoreState()

    can.saveState()
    can.setFillAlpha(1.0)
    ruta_firma = os.path.join(current_app.root_path, 'static', 'img', 'firma3.png')
    can.drawImage(ruta_firma, 190, 500, width=150, height=150, mask='auto')
    can.restoreState()

    can.save()
    packet.seek(0)

    ruta_pdf = os.path.join(current_app.root_path, 'static', 'pdf', 'RecibosOficial9.pdf')
    existing_pdf = PdfReader(open(ruta_pdf, "rb"))
    output = PdfWriter()
    new_pdf = PdfReader(packet)

    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)

    # Armar nombre del archivo base
    
    
    des_gasto = datos.get('des_gasto', 'cliente').strip().replace(" ", "_").replace(",", "").replace(".", "")
    pat_ent = datos.get('pat_ent', 'vehiculo').strip().replace(" ", "_")
    nombre_archivo = f"{des_gasto}_{pat_ent}.pdf"
    #nombre_archivo = f"{datos.get('des_gasto')}_{datos.get('pat_ent')}.pdf"
    ruta_completa = os.path.join(ruta_destino, nombre_archivo)

    # Si el archivo ya existe, agregar _copy1, _copy2, etc.
    contador = 1
    nombre_base, extension = os.path.splitext(nombre_archivo)
    while os.path.exists(ruta_completa):
        nombre_archivo = f"{nombre_base}_copy{contador}{extension}"
        ruta_completa = os.path.join(ruta_destino, nombre_archivo)
        contador += 1

    # Guardar el archivo en el servidor
    with open(ruta_completa, 'wb') as f:
        f.write(output_stream.read())

    # Reiniciar el puntero del stream para enviarlo al navegador
    output_stream.seek(0)

    
    return send_file(
            output_stream,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/pdf'
    )

def formatear_fecha(fecha_str, formato_entrada='%Y-%m-%d', formato_salida='%d/%m/%Y'):
    try:
        return datetime.strptime(fecha_str, formato_entrada).strftime(formato_salida)
    except (ValueError, TypeError):
        return fecha_str

def numero_a_letras(numero):
    entero = int(numero)
    decimal = int(round((numero - entero) * 100))
    if entero == 0:
        resultado_entero = "CERO"
    else:
        resultado_entero = convertir_entero(entero)
    if decimal == 0:
        resultado_decimal = "CON CERO CENTAVOS"
    else:
        resultado_decimal = f"CON {convertir_entero(decimal)} CENTAVOS"
    return f"SON PESOS {resultado_entero} {resultado_decimal}"

def convertir_entero(numero):
    indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
    entero = int(numero)
    if entero == 0:
        return "CERO"
    grupos = []
    while entero > 0:
        grupos.append(entero % 1000)
        entero = entero // 1000
    letras = []
    for i, grupo in enumerate(grupos):
        if grupo == 0:
            continue
        texto = indicador[i][1] if grupo > 1 else indicador[i][0]
        if grupo > 0:
            grupo_letras = convertir_grupo(grupo)
            if texto:
                grupo_letras += " " + texto
            letras.append(grupo_letras)
    resultado = " ".join(reversed(letras))
    reemplazos = {
        "DIECI UNO": "ONCE", "DIECI DOS": "DOCE", "DIECI TRES": "TRECE",
        "DIECI CUATRO": "CATORCE", "DIECI CINCO": "QUINCE",
        "DIECI SEIS": "DIECISEIS", "DIECI SIETE": "DIECISIETE", "DIECI OCHO": "DIECIOCHO", "DIECI NUEVE": "DIECINUEVE",
        "VEINTI UNO": "VEINTIUNO", "VEINTI DOS": "VEINTIDOS", "VEINTI TRES": "VEINTITRES",
        "VEINTI CUATRO": "VEINTICUATRO", "VEINTI CINCO": "VEINTICINCO", "VEINTI SEIS": "VEINTISEIS",
        "VEINTI SIETE": "VEINTISIETE", "VEINTI OCHO": "VEINTIOCHO", "VEINTI NUEVE": "VEINTINUEVE"
    }
    for k, v in reemplazos.items():
        resultado = resultado.replace(k, v)
    return resultado

def convertir_grupo(numero):
    centenas = numero // 100
    decenas = (numero % 100) // 10
    unidades = numero % 10
    letras = []
    if centenas == 1:
        if decenas == 0 and unidades == 0:
            letras.append("CIEN")
        else:
            letras.append("CIENTO")
    elif centenas == 5:
        letras.append("QUINIENTOS")
    elif centenas == 7:
        letras.append("SETECIENTOS")
    elif centenas == 9:
        letras.append("NOVECIENTOS")
    elif centenas > 0:
        letras.append(["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", 
                      "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", 
                      "NOVECIENTOS"][centenas])
    if decenas == 1:
        if unidades == 0:
            letras.append("DIEZ")
        else:
            letras.append(f"DIECI {['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE'][unidades]}")
    elif decenas == 2:
        if unidades == 0:
            letras.append("VEINTE")
        else:
            letras.append(f"VEINTI {['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE'][unidades]}")
    elif decenas > 2:
        letras.append(["", "", "", "TREINTA", "CUARENTA", "CINCUENTA", 
                      "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"][decenas])
        if unidades > 0:
            letras.append(f"Y {['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE'][unidades]}")
    elif unidades > 0:
        letras.append(["", "UNO", "DOS", "TRES", "CUATRO", "CINCO", 
                      "SEIS", "SIETE", "OCHO", "NUEVE"][unidades])
    return " ".join(letras)