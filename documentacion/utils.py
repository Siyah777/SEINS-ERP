import os
import base64
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Documentacion
from django.shortcuts import get_object_or_404

def generar_pdf_documentacion(documentacion_id):
    documentacion = Documentacion.objects.prefetch_related('equipos', 'pasos', 'actividades_post').get(id=documentacion_id)

    template = get_template('documentacion.html')  # Asegúrate que el path coincida

    # Leer y codificar el logo como base64
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    with open(logo_path, 'rb') as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    context = {
        'documentacion': documentacion,
        'logo_base64': logo_base64,
        'empresa': {
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
