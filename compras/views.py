from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Compra
from .utils import generar_pdf_compra
from django.shortcuts import get_list_or_404
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from .utils import calcular_totales_compras
import base64, os
from django.conf import settings

@login_required
def compra_pdf(request, compra_id):
    """
    Vista para generar y descargar el PDF de una cotización.
    Esta vista es llamada desde el admin con el enlace 'Ver PDF'.
    """
    compra = get_object_or_404(Compra, pk=compra_id)

    # Generar el PDF (debe devolver un BytesIO o archivo similar)
    pdf_buffer = generar_pdf_compra(compra_id)
    if not pdf_buffer:
        raise Http404("Error generando el PDF de la cotización.")

    # Retornar la respuesta con el PDF para descarga o vista en navegador
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{compra.correlativo}.pdf"'
    return response

@login_required
def resumen_compras_pdf(request):
    """
    Genera un PDF con resumen de compras seleccionadas.
    Recibe lista de IDs como GET: ?ids=1&ids=2
    """
    ids = request.GET.getlist('ids')
    compras = get_list_or_404(Compra, id__in=ids)

    resumen_compras, total_general_iva = calcular_totales_compras(compras)

    # logo en base64
    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.png')
    logo_base64 = ''
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            logo_base64 = base64.b64encode(f.read()).decode()

    context = {
        "resumen_compras": resumen_compras,
        'total_general_iva': total_general_iva, 
        "logo_base64": logo_base64,
    }

    html = render_to_string("resumen_compras.html", context)
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="resumen_compras.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response, html=html)
    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=500)
    return response