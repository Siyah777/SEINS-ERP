from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse

def render_to_pdf(template_src, context):
    template = get_template(template_src)
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)

    if pdf.err:
        return None

    return result


def generar_pdf_procedimiento(procedimiento):
    context = {
        'procedimiento': procedimiento,
        'pasos': procedimiento.pasos.all(),
        'actividades': procedimiento.actividades_post.all(),
    }

    return render_to_pdf(
        'documentacion/procedimiento_pdf.html',
        context
    )
