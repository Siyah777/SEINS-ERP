from django.contrib import admin
from ..models import Contingencia
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Contingencia)
class ContingenciaAdmin(admin.ModelAdmin):
    list_display = ('correlativo',
    'motivo_contingencia',
    'fecha_envio',               
    'estado_coloreado')
    
    list_per_page = 20
    
    def get_readonly_fields(self, request, obj=None):
        return [
            'correlativo',
            'codigo_generacion',
            'respuesta_firmador',
            'respuesta_hacienda',
            'idenvio_hacienda',
            #'numero_control',
            'sello_recepcion',
            'version_json',
            'fecha_envio',
            'firma',
            'motivo_contingencia',
            'tipo_contingencia',
            'fecha_inicio_contingencia',
            'fecha_fin_contingencia',
            'detalle_contingencia',
            'estado_envio_hacienda',
        ]