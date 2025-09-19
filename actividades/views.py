from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
import os
import base64
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Ordendetrabajo

def obtener_logo_base64():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    with open(logo_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generar_pdf_orden_trabajo(request, orden_id):
    orden = get_object_or_404(Ordendetrabajo, pk=orden_id)
    template = get_template('orden_trabajo_pdf.html')

    context = {
        'orden': orden,
        'logo_base64': obtener_logo_base64(),
    }

    html_content = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename={orden.correlativo}.pdf'

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), dest=result)
    if not pdf.err:
        response.write(result.getvalue())
        return response
    return HttpResponse("Error al generar el PDF", status=500)

