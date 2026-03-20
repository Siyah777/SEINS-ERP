from django.db import models
from django.contrib import admin
from django.db.models import Q, F
from .models import Inventario
from notificaciones.models import Notificacion
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'categoria', 'cantidad', 'stock_minimo', 'proveedor', 'fecha_ingreso', 'fecha_salida', 'inventario_pdf')
    list_filter = ('categoria', 'fecha_ingreso', 'fecha_salida', 'proveedor')
    
    
    def inventario_pdf(self, obj):
        url = reverse('inventario_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">ficha inventario</a>', url)

    inventario_pdf.short_description = 'PDF'

def alertar_stock_bajo(usuario_id=1):
    """
    Genera notificaciones para productos cuyo stock sea menor o igual al stock mínimo.
    
    :param usuario_id: ID del usuario destinatario (default: 1, admin)
    """
    # Filtramos los productos con cantidad <= stock_minimo
    productos_alerta = Inventario.objects.filter(cantidad__lte=F('stock_minimo'))

    for inventario in productos_alerta:
        mensaje = f"¡Producto '{inventario.producto.nombre}' con stock bajo! ({inventario.cantidad} unidades)"
        
        # Evitamos duplicar la notificación si ya existe
        if not Notificacion.objects.filter(mensaje=mensaje, producto=inventario.producto, leido=False).exists():
            Notificacion.objects.create(
                mensaje=mensaje,
                producto=inventario.producto,          # Vinculamos el producto
                usuario_destino_id=usuario_id,         # Usuario destinatario
            )

