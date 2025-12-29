# documentacion/views.py

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Procedimiento
from .utils import generar_pdf_procedimiento

@login_required
def procedimiento_pdf(request, procedimiento_id):
    procedimiento = Procedimiento.objects.prefetch_related(
        'pasos', 'actividades_post', 'equipos'
    ).get(id=procedimiento_id)

    pdf_buffer = generar_pdf_procedimiento(procedimiento)

    if not pdf_buffer:
        return HttpResponse("Error al generar PDF", status=500)

    response = HttpResponse(
        pdf_buffer.getvalue(),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = (
        f'inline; filename="{procedimiento.codigo_documento}.pdf"'
    )

    return response
