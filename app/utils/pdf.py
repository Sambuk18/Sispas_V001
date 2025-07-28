from flask import current_app
from weasyprint import HTML
from datetime import datetime
import os

def generar_pdf_recibo(recibo, template):
    # Renderizar template HTML
    html = template.render(recibo=recibo, fecha=datetime.now())
    
    # Configurar rutas
    uploads_dir = os.path.join(current_app.root_path, 'static/pdf')
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"recibo_{recibo.numero}.pdf"
    filepath = os.path.join(uploads_dir, filename)
    
    # Generar PDF
    HTML(string=html).write_pdf(filepath)
    
    return filename