from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Compra
from .utils import generar_pdf_compra

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
