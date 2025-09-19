import os
import base64
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Cotizacion

def generar_pdf_cotizacion(cotizacion_id):
    cotizacion = Cotizacion.objects.select_related('cliente', 'usuario').get(id=cotizacion_id)

    template = get_template('cotizacion_pdf.html')  # Asegúrate que el path coincida

    # Leer y codificar el logo como base64
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    with open(logo_path, 'rb') as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    context = {
        'cotizacion': cotizacion,
        'logo_base64': logo_base64,
        'empresa': {
            'nombre': "SERVICIOS ESTRATEGICOS INTEGRALES DE INGENIERIA SALVADOREÑOS (SEINSV)",
            'direccion': "Urb. Cumbres de San Bartolo, Senda Villa Toledo, Casa 31 Poligono 59, Tonacatepeque, San Salvador Este",
            'telefono': "(+503) 7537-9826",
            'email': "administracion@seinsv.com",
            # 'nit': "1234-567890-101-2",
            'nrc': "362881-2"
        }
    }

    html = template.render(context)
    pdf_buffer = BytesIO()
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)

    pdf_buffer.seek(0)  # Volver al inicio del buffer
    return pdf_buffer






