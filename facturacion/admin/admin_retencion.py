from django.contrib import admin
from ..models import ComprobanteRetencion
  
from django.utils.html import format_html
from django.urls import reverse

@admin.register(ComprobanteRetencion)
class NComprobanteRetencionAdmin(admin.ModelAdmin):
    list_display = ('correlativo',
    'factura_referencia',
    'cliente',
    'monto_retenido_iva',
    'monto_retenido_renta',
    #'pdf_factura',
    #'json_factura', 
    'estado_coloreado',
    )
    
    list_per_page = 20
    
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
    
    search_fields = ('factura_referencia',)
    list_filter = ('factura_referencia',)
    def get_readonly_fields(self, request, obj=None):
        return [
            'cliente',
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
            'tipo_factura', 
            'condicion_operacion',
            'monto_retenido_iva',
            'monto_retenido_renta',
        
        ]