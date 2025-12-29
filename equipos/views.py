from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Equipo, Herramienta
from .utils import generar_pdf_equipo, generar_pdf_herramienta

@login_required
def equipo_pdf(request, equipo_id):
    """
    Vista para generar y descargar el PDF de un equipo.
    Esta vista es llamada desde el admin con el enlace 'Ver PDF'.
    """
    equipo = get_object_or_404(Equipo, pk=equipo_id)

    # Generar el PDF (debe devolver un BytesIO o archivo similar)
    pdf_buffer = generar_pdf_equipo(equipo_id)
    if not pdf_buffer:
        raise Http404("Error generando el PDF del equipo.")

    # Retornar la respuesta con el PDF para descarga o vista en navegador
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{equipo.codigo_interno}.pdf"'
    return response

@login_required
def herramienta_pdf(request, herramienta_id):
    """
    Vista para generar y descargar el PDF de una herramienta
    Esta vista es llamada desde el admin con el enlace 'Ver PDF'.
    """
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id)

    # Generar el PDF (debe devolver un BytesIO o archivo similar)
    pdf_buffer = generar_pdf_herramienta(herramienta_id)
    if not pdf_buffer:
        raise Http404("Error generando el PDF de la herramienta.")

    # Retornar la respuesta con el PDF para descarga o vista en navegador
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{herramienta.codigo_interno}.pdf"'
    return response