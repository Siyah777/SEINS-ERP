from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Inventario
from .utils import generar_pdf_inventario

@login_required
def inventario_pdf(request, inventario_id):
    """
    Vista para generar y descargar el PDF de un equipo.
    Esta vista es llamada desde el admin con el enlace 'Ver PDF'.
    """
    inventario = get_object_or_404(Inventario, pk=inventario_id)

    # Generar el PDF (debe devolver un BytesIO o archivo similar)
    pdf_buffer = generar_pdf_inventario(inventario_id)
    if not pdf_buffer:
        raise Http404("Error generando el PDF del equipo.")

    # Retornar la respuesta con el PDF para descarga o vista en navegador
    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{Inventario.producto}.pdf"'
    return response
