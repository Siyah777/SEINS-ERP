import os
import base64
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Compra
from decimal import Decimal

def generar_pdf_compra(compra_id):
    compra = Compra.objects.select_related('proveedor').get(id=compra_id)

    template = get_template('compra.html')  # Asegúrate que el path coincida

    # Leer y codificar el logo como base64
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    with open(logo_path, 'rb') as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    context = {
        'compra': compra,
        'logo_base64': logo_base64,
        'empresa': {
        }
    }

    html = template.render(context)
    pdf_buffer = BytesIO()
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)

    pdf_buffer.seek(0)  # Volver al inicio del buffer
    return pdf_buffer

def calcular_totales_compras(con_queryset):
    """
    Recibe un queryset o lista de compras y devuelve:
    - resumen: lista de dict con compra, total_compra_iva y lista unificada de items
    - total_general_iva: suma de todas las compras con IVA incluido
    """
    resumen = []
    total_general_iva = Decimal('0.00')

    for compra in con_queryset:
        items = []

        # Productos
        for p in compra.detalles_productos.all():
            clientes = [c.nombre_empresa for c in p.cliente.all()]
            equipos = [e.nombre for e in p.equipo.all()]
            subtotal_iva = (p.subtotal * Decimal('1.13')).quantize(Decimal('0.01'))
            precio_unitario_iva = (p.precio_unitario * Decimal('1.13')).quantize(Decimal('0.01'))
            items.append({
                "tipo": "Producto",
                "nombre": p.producto.nombre if p.producto else "-",
                "descripcion": p.descripcion_producto,
                "clientes": clientes,
                "cantidad": p.cantidad,
                "equipos": equipos,
                "precio_unitario": precio_unitario_iva,
                "subtotal": subtotal_iva
            })

        # Servicios
        for s in compra.detalles_servicios.all():
            clientes = [c.nombre_empresa for c in s.cliente.all()]
            equipos = [e.nombre for e in s.equipo.all()]
            subtotal_iva = (s.subtotal * Decimal('1.13')).quantize(Decimal('0.01'))
            precio_unitario_iva = (s.precio_unitario * Decimal('1.13')).quantize(Decimal('0.01'))
            items.append({
                "tipo": "Servicio",
                "nombre": s.servicio.nombre if s.servicio else "-",
                "descripcion": s.descripcion_servicio,
                "clientes": clientes,
                "cantidad": s.cantidad,
                "equipos": equipos,
                "precio_unitario": precio_unitario_iva,
                "subtotal": subtotal_iva
            })

        total_compra_iva = sum(item["subtotal"] for item in items)
        total_general_iva += total_compra_iva

        resumen.append({
            "compra": compra,
            "total_compra_iva": total_compra_iva,
            "items": items
        })

    return resumen, total_general_iva