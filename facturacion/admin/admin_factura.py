from django.contrib import admin
from ..models import Factura
from django.utils.html import format_html
from django.urls import reverse
from ..forms import FacturaForm
from django.contrib import messages

def pdf_factura(self, obj):
        if obj.pk:  # Solo si ya fue guardado
            url = reverse('facturacion:descargar_factura_pdf', args=[obj.pk])
            return format_html('<a class="button" href="{}" target="_blank">Descargar Factura</a>', url)
        return "Factura aún no guardada"
pdf_factura.short_description = 'PDF'
    
def json_factura(self, obj):
    if obj.pk:
        url = reverse('facturacion:descargar_factura_json', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Descargar JSON</a>', url)
    return "Factura aún no guardada"
json_factura.short_description = 'JSON'

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    form = FacturaForm
    list_display = ('correlativo',
    'tipo_factura', 
    'cliente', 
    'cotizacion',  
    'total_sin_iva',
    'total_con_iva', 
    'pdf_factura',
    'json_factura', 
    'estado_coloreado',
    )
    
    list_per_page = 20
    
    list_filter = ('fecha_envio', 'cliente', 'estado_envio_hacienda', 'correlativo')
    # ---------- Acciones personalizadas ----------
    def pdf_factura(self, obj):
        if obj.pk:  # Solo si ya fue guardado
            url = reverse('facturacion:descargar_factura_pdf', args=[obj.pk])
            return format_html('<a class="button" href="{}" target="_blank">Descargar Factura</a>', url)
        return "Factura aún no guardada"
    pdf_factura.short_description = 'PDF'
    
    def json_factura(self, obj):
        if obj.pk:
            url = reverse('facturacion:descargar_factura_json', args=[obj.pk])
            return format_html('<a class="button" href="{}" target="_blank">Descargar JSON</a>', url)
        return "Factura aún no guardada"
    json_factura.short_description = 'JSON'
    
    list_filter = ('fecha_envio', 'cliente', 'correlativo')
    def get_readonly_fields(self, request, obj=None):
        return [
            'cliente',
            'ventas_no_sujetas',
            'ventas_exentas',
            'ventas_gravadas',
            'total_sin_iva',
            'iva',
            'iva_retenido',
            'iva_percibido',
            'total_con_iva',
            'total_letras',
            'codigo_generacion',
            'respuesta_firmador',
            'respuesta_hacienda',
            'idenvio_hacienda',
            'numero_control',
            'sello_recepcion',
            'version_dte',
            'version_json',
            'fecha_envio',
            'firma',
            'json_dte',
            'json_firmado',
            'observaciones',
            'estado_envio_hacienda',
            'pdf_factura',
            'json_factura',
            'correlativo',
            'motivo_contingencia',
            'tipo_contingencia',
            'detalle_contingencia',
            'estado_envio_hacienda',
        ]
    
    def save_model(self, request, obj, form, change):
        obj.calcular_totales()  # Recalcula explícitamente
        super().save_model(request, obj, form, change)
        
