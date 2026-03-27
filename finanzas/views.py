from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from .models import Presupuesto
import os
import base64
from django.conf import settings

def obtener_logo_base64():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    with open(logo_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def image_to_base64(field):
    """Convierte un ImageField a base64 para usar en el HTML del PDF."""
    if not field:
        return ""
    try:
        with field.open('rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        return ""

@login_required
def pdf_presupuesto(request, pk):
    presupuesto = Presupuesto.objects.get(pk=pk)
    
    # 🔥 ACTUALIZA ANTES DE GENERAR
    presupuesto.actualizar_totales()

    template = get_template('presupuesto.html')

    context = {
        'presupuesto': presupuesto,
        'ingresos': presupuesto.ingresos.all(),
        'gastos': presupuesto.gastos.all(),
        'logo_base64': obtener_logo_base64(),
    }

    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="presupuesto_{pk}.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response