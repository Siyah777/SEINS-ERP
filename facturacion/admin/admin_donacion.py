from django.contrib import admin
from ..models import ComprobanteDonacion
from django.utils.html import format_html
from django.urls import reverse

@admin.register(ComprobanteDonacion)
class FComprobanteDonacionAdmin(admin.ModelAdmin):
    list_display = ('correlativo',
    'tipo_factura', 
    'donatario',
    'descripcion_donacion',
    'monto',
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
    
    search_fields = ('descripcion_donacion',)
    list_filter = ('descripcion_donacion',)
    def get_readonly_fields(self, request, obj=None):
        return [
            #'ventas_no_sujetas',
            #'ventas_exentas',
            #'ventas_gravadas',
            #'total_sin_iva',
            #'iva',
            #'iva_retenido',
            #'iva_percibido',
            #'total_con_iva',
            #'total_letras',
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
            #'observaciones',
            'estado_envio_hacienda',
            'pdf_factura',
            'json_factura',
            'correlativo',
            'tipo_factura', 
            #'cotizacion',
            #'condicion_operacion',
        ]
        