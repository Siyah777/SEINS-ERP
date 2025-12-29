from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Documentacion
from .utils import generar_pdf_documentacion
from django.shortcuts import get_object_or_404

@login_required
def documentacion_pdf(request, documentacion_id):
    documentacion = get_object_or_404(Documentacion, pk=documentacion_id)

    pdf_buffer = generar_pdf_documentacion(documentacion.id)

    if not pdf_buffer:
        return HttpResponse("Error al generar PDF", status=500)

    response = HttpResponse(
        pdf_buffer.getvalue(),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = (
        f'inline; filename="{documentacion.codigo_documento}.pdf"'
    )

    return response
