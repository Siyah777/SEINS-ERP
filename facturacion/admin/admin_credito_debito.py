from django.contrib import admin
from ..models import NotaCreditoDebito
from django.utils.html import format_html
from django.urls import reverse
#from ..forms import FacturaForm

@admin.register(NotaCreditoDebito)
class NotaCreditoAdmin(admin.ModelAdmin):
    list_display = ('correlativo',
    'tipo_nota',
    'cliente',
    'factura_referencia',
    'motivo',
    'nuevo_monto',
    #'pdf_factura',
    #'json_factura',
    'estado_coloreado')
    
    list_per_page = 20
    
    def pdf_factura(self, obj):
        if obj.pk:  # Solo si ya fue guardado
            url = reverse('facturacion:descargar_factura_pdf', args=[obj.pk])
            return format_html('<a class="button" href="{}" target="_blank">Descargar Nota</a>', url)
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
            'nuevo_monto_letras',
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
            'estado_envio_hacienda',
            'pdf_factura',
            'json_factura',
            'correlativo',
            'tipo_nota',
        ]