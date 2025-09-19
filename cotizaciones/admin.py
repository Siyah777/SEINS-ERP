from django.contrib import admin
from .models import Cotizacion, DetalleCotizacionProductos, DetalleCotizacionServicios 
from .models import ListaDeMateriales
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

class DetalleCotizacionProductosInline(admin.TabularInline):
    model = DetalleCotizacionProductos
    extra = 1

class DetalleCotizacionServiciosInline(admin.TabularInline):
    model = DetalleCotizacionServicios
    extra = 1

class ListaDeMaterialesInline(admin.StackedInline): #StackedInline
    model = ListaDeMateriales
    extra = 1

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ("correlativo", "cliente", "Descripcion", "fecha", "estatus_coloreado", "total_con_dolar", "ver_pdf")
    list_per_page = 20
    readonly_fields = ("total", "total_iva", "correlativo")
    def total_con_dolar(self, obj):
     return mark_safe(f"${float(obj.total_iva):.2f}")
    total_con_dolar.short_description = 'Total ($)'
    
    def total_formateado(self, obj):
        return mark_safe(f"${float(obj.total_iva):.2f}")
    total_formateado.short_description = 'Total ($)'
    
    def estatus_coloreado(self, obj):
        colores = {
            'pendiente': 'orange',
            'aprobada': 'green',
            'no_aprobada': 'red',
        }
        color = colores.get(obj.estatus, 'black')
        return format_html(f'<strong style="color: {color};">{obj.get_estatus_display()}</strong>')
    
    def ver_pdf(self, obj):
        url = reverse('cotizacion_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Ver Cotización</a>', url)

    ver_pdf.short_description = 'PDF'

    estatus_coloreado.short_description = 'Estatus'
    inlines = [DetalleCotizacionProductosInline, DetalleCotizacionServiciosInline, ListaDeMaterialesInline]

admin.site.register(DetalleCotizacionProductos)
admin.site.register(DetalleCotizacionServicios)
admin.site.register(ListaDeMateriales)
