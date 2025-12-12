from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
import os
import base64
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Ordendetrabajo
from django.core.files.base import ContentFile
from recursos_humanos.models import Empleado
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from urllib.parse import urlencode


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

def generar_pdf_orden_trabajo(request, orden_id):
    orden = get_object_or_404(Ordendetrabajo, pk=orden_id)
    template = get_template('orden_trabajo_pdf.html')
    
    # 🔹 Obtener técnico principal (el primero asignado)
    tecnico = orden.personal_asignado.first()
    firma_tecnico_base64 = None
    nombre_tecnico = "No asignado"
    
    if tecnico:
        nombre_tecnico = tecnico.get_full_name() or tecnico.username
        try:
            empleado = Empleado.objects.get(usuario=tecnico)
            if empleado.firma_tecnico_img:
                firma_tecnico_base64 = image_to_base64(empleado.firma_tecnico_img)
        except Empleado.DoesNotExist:
            pass

    # 🔹 Si el técnico no tiene firma, usar una firma genérica o sello
    if not firma_tecnico_base64:
        ruta_generica = os.path.join("static", "img", "firma_generica.png")
        if os.path.exists(ruta_generica):
            with open(ruta_generica, "rb") as f:
                firma_tecnico_base64 = base64.b64encode(f.read()).decode("utf-8")
        else:
            firma_tecnico_base64 = None  # No hay imagen, se mostrará texto

    context = {
        'orden': orden,
        'logo_base64': obtener_logo_base64(),
        'imagen_antes_1': image_to_base64(orden.imagen_antes_1),
        'imagen_antes_2': image_to_base64(orden.imagen_antes_2),
        'imagen_despues_1': image_to_base64(orden.imagen_despues_1),
        'imagen_despues_2': image_to_base64(orden.imagen_despues_2),
        'firma_cliente': image_to_base64(orden.firma_cliente_img),
        'firma_tecnico': firma_tecnico_base64,
        
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

def calendario_eventos(request):
    actividades = Ordendetrabajo.objects.filter(
        estatus="programado",
    )
    
    eventos = []
    for act in actividades:
        if act.fecha_inicio is None:
            continue  # o poner fecha por defecto
        fecha = act.fecha_inicio.strftime("%Y-%m-%d")

        # Construir URL filtrada en el admin
        url_filtrada = reverse("admin:actividades_ordendetrabajo_changelist") + "?" + urlencode({
            "estatus__exact": "programado",
            "fecha_inicio__gte": fecha,
            "fecha_inicio__lte": fecha,
            "q": "",
        })
        
        eventos.append({
            "title": getattr(act, "titulo", f"{act.correlativo}"),
            "start": act.fecha_inicio.isoformat(),
            "url": url_filtrada,
            "extendedProps": {
                "descripcion": getattr(act, "descripcion", ""),
            }
        })
    
    return JsonResponse(eventos, safe=False)
